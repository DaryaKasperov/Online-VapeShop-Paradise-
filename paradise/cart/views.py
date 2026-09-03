from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from catalog.models import Product, FlavorStock, ColorStock, Order
from .models import CartItem


def cart_view(request):
    """Страница корзины"""
    return render(request, 'cart/cart.html')


def cart_add(request, product_id):
    """Добавление товара в корзину"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        action = request.POST.get('action', 'cart')

        # Получаем выбранные вкусы
        selected_flavors = request.POST.get('selected_flavors', '')
        selected_colors = request.POST.get('selected_colors', '')

        # Получаем или создаем сессию
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        added_count = 0

        # Добавляем каждый выбранный вкус отдельно
        if selected_flavors:
            for item in selected_flavors.split(','):
                if ':' in item:
                    flavor, quantity = item.split(':')
                    quantity = int(quantity)

                    # Проверяем остаток
                    try:
                        flavor_stock = product.flavor_stocks.get(flavor=flavor)
                        if flavor_stock.quantity < quantity:
                            messages.warning(request, f'Вкуса "{flavor}" доступно только {flavor_stock.quantity} шт.')
                            continue
                    except FlavorStock.DoesNotExist:
                        continue

                    # Добавляем в корзину
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

        # Добавляем каждый выбранный цвет отдельно
        if selected_colors:
            for item in selected_colors.split(','):
                if ':' in item:
                    color, quantity = item.split(':')
                    quantity = int(quantity)

                    # Проверяем остаток
                    try:
                        color_stock = product.color_stocks.get(color=color)
                        if color_stock.quantity < quantity:
                            messages.warning(request, f'Цвета "{color}" доступно только {color_stock.quantity} шт.')
                            continue
                    except ColorStock.DoesNotExist:
                        continue

                    # Добавляем в корзину
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

        # Если есть простое количество (без вкусов и цветов)
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
            messages.success(request, f'Товары добавлены в корзину!')
        else:
            messages.error(request, 'Не удалось добавить товары в корзину')

        # Если "Купить сейчас" — перенаправляем в корзину для оформления
        if action == 'order':
            return redirect('cart:cart_view')

        return redirect('cart:cart_view')

    return redirect('catalog:product_list')

def cart_remove(request, item_id):
    """Удаление товара из корзины"""
    session_key = request.session.session_key
    if session_key:
        cart_item = get_object_or_404(CartItem, id=item_id, session_key=session_key)
        cart_item.delete()
        messages.success(request, 'Товар удален из корзины')

    return redirect('cart:cart_view')


def cart_update(request, item_id):
    """Обновление количества товара в корзине"""
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

    return redirect('cart:cart_view')


def cart_checkout(request):
    """Оформление заказа из корзины"""
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

        # Создаем заказ для каждого товара в корзине
        for item in cart_items:
            # Проверяем остатки
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

            # Создаем заказ
            Order.objects.create(
                product=item.product,
                flavor=item.flavor or 'Не выбран',
                color=item.color or 'Не выбран',
                quantity=item.quantity,
                telegram=telegram,
                comment=comment
            )

        # Очищаем корзину
        cart_items.delete()

        messages.success(request, 'Заказ оформлен! Мы свяжемся с вами в Telegram.')
        return redirect('catalog:product_list')

    return redirect('cart:cart_view')


def cart_clear(request):
    """Очистка корзины"""
    session_key = request.session.session_key
    if session_key:
        CartItem.objects.filter(session_key=session_key).delete()
        messages.info(request, 'Корзина очищена')

    return redirect('cart:cart_view')