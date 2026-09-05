from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.apps import apps
import os
import requests

# ✅ Импорты из catalog
from catalog.models import Product, FlavorStock, ColorStock, Order, OrderItem

# ✅ Импорт из текущего приложения
from .models import CartItem


def cart_view(request):
    """Страница корзины"""
    return render(request, 'cart/cart.html')


def cart_add(request, product_id):
    """Добавление товара в корзину"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        action = request.POST.get('action', 'cart')

        selected_flavors = request.POST.get('selected_flavors', '')
        selected_colors = request.POST.get('selected_colors', '')

        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        added_count = 0

        # Добавляем вкусы
        if selected_flavors:
            for item in selected_flavors.split(','):
                if ':' in item:
                    flavor, quantity = item.split(':')
                    quantity = int(quantity)

                    try:
                        flavor_stock = product.flavor_stocks.get(flavor=flavor)
                        if flavor_stock.quantity < quantity:
                            messages.warning(request, f'Вкуса "{flavor}" доступно только {flavor_stock.quantity} шт.')
                            continue
                    except FlavorStock.DoesNotExist:
                        continue

                    cart_item, created = CartItem.objects.get_or_create(
                        session_key=session_key,
                        product=product,
                        flavor=flavor,
                        color='',
                        defaults={'quantity': quantity}
                    )
                    if not created:
                        cart_item.quantity += quantity
                        cart_item.save()
                    added_count += 1

        # Добавляем цвета
        if selected_colors:
            for item in selected_colors.split(','):
                if ':' in item:
                    color, quantity = item.split(':')
                    quantity = int(quantity)

                    try:
                        color_stock = product.color_stocks.get(color=color)
                        if color_stock.quantity < quantity:
                            messages.warning(request, f'Цвета "{color}" доступно только {color_stock.quantity} шт.')
                            continue
                    except ColorStock.DoesNotExist:
                        continue

                    cart_item, created = CartItem.objects.get_or_create(
                        session_key=session_key,
                        product=product,
                        flavor='',
                        color=color,
                        defaults={'quantity': quantity}
                    )
                    if not created:
                        cart_item.quantity += quantity
                        cart_item.save()
                    added_count += 1

        # Простое количество
        if not selected_flavors and not selected_colors:
            quantity = int(request.POST.get('quantity', 1))
            cart_item, created = CartItem.objects.get_or_create(
                session_key=session_key,
                product=product,
                flavor='',
                color='',
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            added_count = 1

        if added_count > 0:
            messages.success(request, 'Товары добавлены в корзину!')
        else:
            messages.error(request, 'Не удалось добавить товары в корзину')

        if action == 'order':
            return redirect('cart:cart_view')

        return redirect('cart:cart_view')

    return redirect('catalog:product_list')


def cart_update(request, item_id):
    """Обновление количества товара в корзине (AJAX)"""
    if request.method == 'POST':
        session_key = request.session.session_key
        if session_key:
            cart_item = get_object_or_404(CartItem, id=item_id, session_key=session_key)
            quantity = int(request.POST.get('quantity', 1))

            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
            else:
                cart_item.delete()

            cart_items = CartItem.objects.filter(session_key=session_key)
            total_items = sum(item.quantity for item in cart_items)
            total_price = sum(item.get_total_price() for item in cart_items)

            return JsonResponse({
                'success': True,
                'quantity': cart_item.quantity if quantity > 0 else 0,
                'item_total': float(cart_item.get_total_price()) if quantity > 0 else 0,
                'cart_total': float(total_price),
                'cart_count': total_items,
            })

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


def cart_remove(request, item_id):
    """Удаление товара из корзины (AJAX)"""
    if request.method == 'POST':
        session_key = request.session.session_key
        if session_key:
            cart_item = get_object_or_404(CartItem, id=item_id, session_key=session_key)
            cart_item.delete()

            cart_items = CartItem.objects.filter(session_key=session_key)
            total_items = sum(item.quantity for item in cart_items)
            total_price = sum(item.get_total_price() for item in cart_items)

            return JsonResponse({
                'success': True,
                'cart_total': float(total_price),
                'cart_count': total_items,
            })

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


def send_telegram_notification(order):
    """Отправка уведомления о заказе в Telegram"""
    bot_token = os.getenv('TG_BOT_TOKEN')
    chat_id = os.getenv('TG_CHAT_ID')

    if not bot_token or not chat_id:
        print('❌ Ошибка: TG_BOT_TOKEN или TG_CHAT_ID не заданы в .env')
        return False

    items_text = ""
    for item in order.items.all():
        variant = ""
        if item.flavor and item.flavor != 'Не выбран':
            variant = f" ({item.flavor})"
        elif item.color and item.color != 'Не выбран':
            variant = f" ({item.color})"
        items_text += f"\n• {item.product.name}{variant} — {item.quantity} шт. × {item.price} BYN"

    telegram_link = f"https://t.me/{order.telegram}" if order.telegram else ""

    message = f"""
🛍️ *НОВЫЙ ЗАКАЗ!* (№{order.id})

📦 *Товары:*{items_text}

💰 *Итого:* {order.total_price} BYN
📝 *Комментарий:* {order.comment or 'Нет'}

👤 *Покупатель:* [{order.telegram}]({telegram_link})
📅 *Дата:* {order.created_at.strftime('%d.%m.%Y %H:%M')}
    """

    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }

    try:
        response = requests.post(url, data=data, timeout=10)
        print(f'✅ Telegram ответ: {response.text}')
        return True
    except Exception as e:
        print(f'❌ Ошибка отправки в Telegram: {e}')
        return False


def cart_checkout(request):
    """Оформление заказа из корзины (ОДИН заказ)"""
    session_key = request.session.session_key
    if not session_key:
        return redirect('cart:cart_view')

    cart_items = CartItem.objects.filter(session_key=session_key)

    if not cart_items:
        messages.error(request, 'Корзина пуста')
        return redirect('cart:cart_view')

    if request.method == 'POST':
        telegram = request.POST.get('telegram', '').strip()
        comment = request.POST.get('comment', '')

        if not telegram:
            messages.error(request, 'Пожалуйста, введите ваш Telegram-ник')
            return redirect('cart:cart_view')

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    telegram=telegram,
                    comment=comment,
                    total_price=0
                )

                total_price = 0

                for item in cart_items:
                    if item.flavor:
                        try:
                            flavor_stock = FlavorStock.objects.get(
                                product=item.product,
                                flavor=item.flavor
                            )
                            if flavor_stock.quantity < item.quantity:
                                messages.error(request, f'Вкуса "{item.flavor}" недостаточно ({flavor_stock.quantity} шт.)')
                                return redirect('cart:cart_view')
                            flavor_stock.quantity -= item.quantity
                            flavor_stock.save()
                        except FlavorStock.DoesNotExist:
                            messages.error(request, f'Вкус "{item.flavor}" не найден')
                            return redirect('cart:cart_view')

                    if item.color:
                        try:
                            color_stock = ColorStock.objects.get(
                                product=item.product,
                                color=item.color
                            )
                            if color_stock.quantity < item.quantity:
                                messages.error(request, f'Цвета "{item.color}" недостаточно ({color_stock.quantity} шт.)')
                                return redirect('cart:cart_view')
                            color_stock.quantity -= item.quantity
                            color_stock.save()
                        except ColorStock.DoesNotExist:
                            messages.error(request, f'Цвет "{item.color}" не найден')
                            return redirect('cart:cart_view')

                    item_price = float(item.product.price) * item.quantity
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        flavor=item.flavor or 'Не выбран',
                        color=item.color or 'Не выбран',
                        quantity=item.quantity,
                        price=item.product.price
                    )
                    total_price += item_price

                order.total_price = total_price
                order.save()

                cart_items.delete()

                send_telegram_notification(order)

                messages.success(request, f' Заказ оформлен! Мы свяжемся с вами в телеграмм.')
                return redirect('catalog:product_list')

        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')
            return redirect('cart:cart_view')

    return redirect('cart:cart_view')


def cart_clear(request):
    """Очистка корзины"""
    session_key = request.session.session_key
    if session_key:
        CartItem.objects.filter(session_key=session_key).delete()
        messages.info(request, 'Корзина очищена')

    return redirect('cart:cart_view')