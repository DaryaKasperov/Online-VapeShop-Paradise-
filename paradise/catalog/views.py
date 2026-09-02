from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import Category, Product, Order, Review, FlavorStock, ColorStock
from .filters import ProductFilter
from .forms import ReviewForm, OrderForm
import requests
import os


def product_list(request, category_slug=None):
    """Главная страница и список товаров с фильтрацией"""
    categories = Category.objects.all()

    # Получаем все товары, которые есть в наличии
    products = Product.objects.filter(in_stock=True)

    # Фильтруем товары: оставляем только те, у которых есть что-то в наличии
    filtered_products = []
    for product in products:
        if product.has_stock():
            filtered_products.append(product.id)

    products = products.filter(id__in=filtered_products)

    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    category_id = request.GET.get('category')
    if category_id and not category:
        try:
            category = get_object_or_404(Category, id=category_id)
        except:
            pass

    filter = ProductFilter(request.GET, queryset=products)
    products = filter.qs

    context = {
        'categories': categories,
        'category': category,
        'filter': filter,
        'products': products,
    }
    return render(request, 'catalog/index.html', context)


def product_detail(request, slug):
    """Страница одного товара с отзывами, вкусами и цветами"""
    try:
        product = get_object_or_404(Product, slug=slug, in_stock=True)

        # Проверяем, есть ли у товара что-то в наличии
        if not product.has_stock():
            from django.http import Http404
            raise Http404("Товар временно недоступен")

        reviews = product.reviews.filter(is_approved=True).order_by('-created_at')

        # Получаем вкусы и цвета с остатками
        flavors = product.flavor_stocks.filter(quantity__gt=0)
        colors = product.color_stocks.filter(quantity__gt=0)

        # Проверяем, есть ли вкусы или цвета
        has_flavors = flavors.exists()
        has_colors = colors.exists()
        has_simple_quantity = product.quantity > 0

        if request.method == 'POST':
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.product = product
                review.is_approved = True
                review.save()
                messages.success(request, 'Спасибо за ваш отзыв!')
                return redirect('catalog:product_detail', slug=product.slug)
        else:
            form = ReviewForm()

        context = {
            'product': product,
            'flavors': flavors,
            'colors': colors,
            'has_flavors': has_flavors,
            'has_colors': has_colors,
            'has_simple_quantity': has_simple_quantity,
            'reviews': reviews,
            'review_form': form,
            'order_form': OrderForm(),
        }
        return render(request, 'catalog/product_detail.html', context)
    except Http404:
        raise
    except Exception as e:
        import traceback
        error_text = traceback.format_exc()
        print(error_text)
        return HttpResponse(f"<pre>{error_text}</pre>", status=500)

def send_telegram_notification(order, product, flavors_text, colors_text, quantity):
    """Отправка уведомления в Telegram"""
    bot_token = os.getenv('TG_BOT_TOKEN')
    chat_id = os.getenv('TG_CHAT_ID')

    if not bot_token or not chat_id:
        print('❌ Ошибка: TG_BOT_TOKEN или TG_CHAT_ID не заданы в .env')
        return False

    flavor_text = f"\n🍽️ *Вкусы:* {flavors_text}" if flavors_text else ""
    color_text = f"\n🎨 *Цвета:* {colors_text}" if colors_text else ""
    quantity_text = f"\n📦 *Общее количество:* {quantity}" if quantity else ""
    telegram_link = f"https://t.me/{order.telegram}" if order.telegram else ""

    message = f"""
🛍️ *НОВЫЙ ЗАКАЗ!*

📦 *Товар:* {product.name}
{flavor_text}
{color_text}
{quantity_text}
📝 *Комментарий:* {order.comment or 'Нет'}

👤 *Покупатель:* [{order.telegram}]({telegram_link})
    """

    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }

    try:
        response = requests.post(url, data=data)
        print(f'✅ Telegram ответ: {response.text}')
        return True
    except Exception as e:
        print(f'❌ Ошибка отправки в Telegram: {e}')
        return False


def order_create(request, product_id):
    """Обработка заказа с выбором вкуса ИЛИ цвета"""
    try:
        product = get_object_or_404(Product, id=product_id)

        if request.method == 'POST':
            telegram = request.POST.get('telegram', '').strip()
            comment = request.POST.get('comment', '')
            selected_flavors = request.POST.get('selected_flavors', '')
            selected_colors = request.POST.get('selected_colors', '')
            simple_quantity = request.POST.get('quantity', 1)

            print(f"📝 Заказ: telegram={telegram}, flavors={selected_flavors}, colors={selected_colors}")

            # Проверяем, есть ли вкусы и цвета у товара
            has_flavors = product.flavor_stocks.exists()
            has_colors = product.color_stocks.exists()

            # Если есть вкусы или цвета — используем их логику
            if has_flavors or has_colors:
                # Разбираем выбранные вкусы
                flavor_list = []
                if selected_flavors:
                    for item in selected_flavors.split(','):
                        if ':' in item:
                            flavor, qty = item.split(':')
                            flavor_list.append({'flavor': flavor, 'quantity': int(qty)})

                # Разбираем выбранные цвета
                color_list = []
                if selected_colors:
                    for item in selected_colors.split(','):
                        if ':' in item:
                            color, qty = item.split(':')
                            color_list.append({'color': color, 'quantity': int(qty)})

                # Проверяем: должен быть выбран хотя бы один вкус ИЛИ цвет
                if not flavor_list and not color_list:
                    messages.error(request, '❌ Пожалуйста, выберите хотя бы один вкус или цвет')
                    return redirect('catalog:product_detail', slug=product.slug)

                # Проверяем остатки по вкусам
                total_quantity = 0
                for item in flavor_list:
                    try:
                        flavor_stock = product.flavor_stocks.get(flavor=item['flavor'])
                        if flavor_stock.quantity < item['quantity']:
                            messages.error(request,
                                           f'Вкуса "{item["flavor"]}" доступно только {flavor_stock.quantity} шт.')
                            return redirect('catalog:product_detail', slug=product.slug)
                        total_quantity += item['quantity']
                    except FlavorStock.DoesNotExist:
                        messages.error(request, f'Вкус "{item["flavor"]}" не найден')
                        return redirect('catalog:product_detail', slug=product.slug)

                # Проверяем остатки по цветам
                for item in color_list:
                    try:
                        color_stock = product.color_stocks.get(color=item['color'])
                        if color_stock.quantity < item['quantity']:
                            messages.error(request,
                                           f'Цвета "{item["color"]}" доступно только {color_stock.quantity} шт.')
                            return redirect('catalog:product_detail', slug=product.slug)
                    except ColorStock.DoesNotExist:
                        messages.error(request, f'Цвет "{item["color"]}" не найден')
                        return redirect('catalog:product_detail', slug=product.slug)

                # Уменьшаем остатки по вкусам
                for item in flavor_list:
                    flavor_stock = product.flavor_stocks.get(flavor=item['flavor'])
                    flavor_stock.quantity -= item['quantity']
                    flavor_stock.save()

                # Уменьшаем остатки по цветам
                for item in color_list:
                    color_stock = product.color_stocks.get(color=item['color'])
                    color_stock.quantity -= item['quantity']
                    color_stock.save()

                # Создаем заказ
                flavors_text = ', '.join([f"{item['flavor']} ({item['quantity']} шт.)" for item in
                                          flavor_list]) if flavor_list else 'Не выбран'
                colors_text = ', '.join(
                    [f"{item['color']} ({item['quantity']} шт.)" for item in color_list]) if color_list else 'Не выбран'

                order = Order.objects.create(
                    product=product,
                    telegram=telegram,
                    flavor=flavors_text,
                    color=colors_text,
                    quantity=total_quantity,
                    comment=comment
                )

                send_telegram_notification(order, product, flavors_text, colors_text, total_quantity)

            else:
                # Для товаров без вкусов и цветов — простое количество
                try:
                    quantity = int(simple_quantity)
                    if quantity < 1:
                        quantity = 1
                    if quantity > product.quantity:
                        messages.error(request, f'Доступно только {product.quantity} шт.')
                        return redirect('catalog:product_detail', slug=product.slug)
                except:
                    quantity = 1

                # Уменьшаем количество
                product.quantity -= quantity
                product.save()

                order = Order.objects.create(
                    product=product,
                    telegram=telegram,
                    flavor='Не выбран',
                    color='Не выбран',
                    quantity=quantity,
                    comment=comment
                )

                send_telegram_notification(order, product, 'Не выбран', 'Не выбран', quantity)

            messages.success(request, f'Спасибо! Ваш заказ на "{product.name}" принят!')

            # ========== ПЕРЕНАПРАВЛЕНИЕ НА ГЛАВНУЮ ==========
            return redirect('catalog:product_list')

        return redirect('catalog:product_detail', slug=product.slug)
    except Exception as e:
        import traceback
        error_text = traceback.format_exc()
        print(error_text)
        return HttpResponse(f"<pre>{error_text}</pre>", status=500)
