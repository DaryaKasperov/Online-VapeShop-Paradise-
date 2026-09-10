from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.db.models import F
from decimal import Decimal
import os
import requests

# ✅ Импорты из catalog
from catalog.models import (
    Product, FlavorStock, ColorStock,
    Order, OrderItem, BlockedUser, PromoCode
)

# ✅ Импорт из текущего приложения
from .models import CartItem


# ============================================================
# КОРЗИНА
# ============================================================

def cart_view(request):
    """Страница корзины"""
    session_key = request.session.session_key
    cart_items = []
    cart_total_price = 0

    if session_key:
        cart_items = CartItem.objects.filter(session_key=session_key).select_related('product')
        cart_total_price = sum(item.get_total_price() for item in cart_items)

        # Добавляем max_quantity к каждому товару
        for item in cart_items:
            item.max_quantity = get_max_quantity(item)

    return render(request, 'cart/cart.html', {
        'cart_items': cart_items,
        'cart_total_price': cart_total_price,
    })


def get_max_quantity(cart_item):
    """Возвращает максимально доступное количество для позиции корзины."""
    product = cart_item.product

    if cart_item.flavor:
        try:
            flavor_stock = product.flavor_stocks.get(flavor=cart_item.flavor)
            return flavor_stock.quantity
        except FlavorStock.DoesNotExist:
            return 0

    if cart_item.color:
        try:
            color_stock = product.color_stocks.get(color=cart_item.color)
            return color_stock.quantity
        except ColorStock.DoesNotExist:
            return 0

    return product.quantity


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
        if not session_key:
            return JsonResponse({'success': False, 'error': 'Сессия не найдена'}, status=400)

        cart_item = get_object_or_404(CartItem, id=item_id, session_key=session_key)
        quantity = int(request.POST.get('quantity', 1))

        # ✅ Ограничиваем по доступному количеству
        max_qty = get_max_quantity(cart_item)
        if quantity > max_qty:
            quantity = max_qty

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
            'max_quantity': max_qty,
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


# ============================================================
# ПРОМОКОДЫ
# ============================================================

@require_POST
def apply_promo(request):
    """AJAX-проверка промокода."""
    code = request.POST.get('code', '').strip().upper()

    if not code:
        return JsonResponse({'success': False, 'error': 'Введите промокод'})

    session_key = request.session.session_key
    if not session_key:
        return JsonResponse({'success': False, 'error': 'Корзина пуста'})

    cart_items = CartItem.objects.filter(session_key=session_key)
    if not cart_items.exists():
        return JsonResponse({'success': False, 'error': 'Корзина пуста'})

    total_price = sum(Decimal(str(item.get_total_price())) for item in cart_items)

    try:
        promo = PromoCode.objects.get(code__iexact=code)
    except PromoCode.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Промокод не найден'})

    is_valid, message = promo.is_valid(total_price)
    if not is_valid:
        return JsonResponse({'success': False, 'error': message})

    discount = promo.calculate_discount(total_price)
    new_total = max(Decimal('0'), total_price - discount)

    # ✅ Сохраняем промокод и скидку в сессии
    request.session['promo_code'] = promo.code
    request.session['promo_discount'] = str(discount)

    return JsonResponse({
        'success': True,
        'message': f'Промокод применён! Скидка: {discount:.2f} BYN',
        'discount': float(discount),
        'new_total': float(new_total),
        'promo_code': promo.code,
    })


# ============================================================
# TELEGRAM
# ============================================================

def send_telegram_notification(order):
    """Отправка уведомления о заказе в Telegram."""
    bot_token = os.getenv('TG_BOT_TOKEN')
    chat_id = os.getenv('TG_CHAT_ID')

    if not bot_token or not chat_id:
        print('❌ Ошибка: TG_BOT_TOKEN или TG_CHAT_ID не заданы')
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

    # ✅ Блок со скидкой
    discount_text = ""
    if order.discount and float(order.discount) > 0:
        discount_text = f"\n🎁 *Скидка:* -{order.discount} BYN"
        if order.promo_code:
            discount_text += f" (промокод: `{order.promo_code}`)"

    message = f"""
🛍️ *НОВЫЙ ЗАКАЗ!* (№{order.id})

📦 *Товары:*{items_text}

💰 *Итого:* {order.total_price} BYN{discount_text}
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


def is_user_blocked(telegram):
    """Проверка, заблокирован ли пользователь."""
    if not telegram:
        return False
    return BlockedUser.objects.filter(telegram=telegram, is_active=True).exists()


# ============================================================
# ОФОРМЛЕНИЕ ЗАКАЗА
# ============================================================

def cart_checkout(request):
    """Оформление заказа из корзины с проверкой блокировки."""
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

        if is_user_blocked(telegram):
            messages.error(request, f'❌ Пользователь @{telegram} заблокирован. Обратитесь к администратору.')
            return redirect('cart:cart_view')

        # ✅ Получаем промокод и скидку из сессии
        promo_code = request.session.get('promo_code', '')
        discount = Decimal(str(request.session.get('promo_discount', '0')))

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    telegram=telegram,
                    comment=comment,
                    total_price=0,
                    promo_code=promo_code,
                    discount=discount,
                )

                total_price = 0

                for item in cart_items:
                    # Списываем вкусы
                    if item.flavor:
                        try:
                            flavor_stock = FlavorStock.objects.select_for_update().get(
                                product=item.product,
                                flavor=item.flavor
                            )
                            if flavor_stock.quantity < item.quantity:
                                messages.error(request, f'Вкуса "{item.flavor}" недостаточно ({flavor_stock.quantity} шт.)')
                                return redirect('cart:cart_view')
                            flavor_stock.quantity = F('quantity') - item.quantity
                            flavor_stock.save(update_fields=['quantity'])
                        except FlavorStock.DoesNotExist:
                            messages.error(request, f'Вкус "{item.flavor}" не найден')
                            return redirect('cart:cart_view')

                    # Списываем цвета
                    if item.color:
                        try:
                            color_stock = ColorStock.objects.select_for_update().get(
                                product=item.product,
                                color=item.color
                            )
                            if color_stock.quantity < item.quantity:
                                messages.error(request, f'Цвета "{item.color}" недостаточно ({color_stock.quantity} шт.)')
                                return redirect('cart:cart_view')
                            color_stock.quantity = F('quantity') - item.quantity
                            color_stock.save(update_fields=['quantity'])
                        except ColorStock.DoesNotExist:
                            messages.error(request, f'Цвет "{item.color}" не найден')
                            return redirect('cart:cart_view')

                    # Списываем простое количество
                    if not item.flavor and not item.color:
                        product = Product.objects.select_for_update().get(id=item.product.id)
                        if product.quantity < item.quantity:
                            messages.error(request, f'Товара "{product.name}" недостаточно ({product.quantity} шт.)')
                            return redirect('cart:cart_view')
                        product.quantity = F('quantity') - item.quantity
                        product.save(update_fields=['quantity'])

                    # Создаём позицию заказа
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

                # ✅ Применяем скидку
                if discount > 0:
                    total_price = max(0, float(total_price) - float(discount))

                order.total_price = total_price
                order.save()

                # ✅ Увеличиваем счётчик использований промокода
                if promo_code:
                    try:
                        promo = PromoCode.objects.select_for_update().get(code__iexact=promo_code)
                        promo.used_count = F('used_count') + 1
                        promo.save(update_fields=['used_count'])
                    except PromoCode.DoesNotExist:
                        pass

                # Обновляем статус наличия
                for item in cart_items:
                    item.product.refresh_from_db()
                    item.product.in_stock = item.product.has_stock()
                    item.product.save(update_fields=['in_stock'])

                cart_items.delete()

                # ✅ Очищаем промокод из сессии
                request.session.pop('promo_code', None)
                request.session.pop('promo_discount', None)

                send_telegram_notification(order)

                messages.success(request, 'Заказ оформлен! Мы свяжемся с вами в Telegram.')
                return redirect('catalog:product_list')

        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')
            return redirect('cart:cart_view')

    return redirect('cart:cart_view')


def cart_clear(request):
    """Очистка корзины."""
    session_key = request.session.session_key
    if session_key:
        CartItem.objects.filter(session_key=session_key).delete()
        request.session.pop('promo_code', None)
        request.session.pop('promo_discount', None)
        messages.info(request, 'Корзина очищена')

    return redirect('cart:cart_view')