from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Category, Product, Order, Review
from .filters import ProductFilter
from .forms import ReviewForm, OrderForm  # ← Добавьте OrderForm
import requests
import os


def product_list(request, category_slug=None):
    """Главная страница и список товаров"""
    categories = Category.objects.all()
    products = Product.objects.filter(in_stock=True)

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
    """Страница одного товара с отзывами"""
    product = get_object_or_404(Product, slug=slug, in_stock=True)
    reviews = product.reviews.filter(is_approved=True).order_by('-created_at')

    # Получаем списки вкусов и цветов
    flavors_list = product.get_flavors_list()
    colors_list = product.get_colors_list()

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
        'flavors': flavors_list,
        'colors': colors_list,  # ← Добавьте цвета
        'reviews': reviews,
        'review_form': form,
        'order_form': OrderForm(),
    }
    return render(request, 'catalog/product_detail.html', context)
def order_create(request, product_id):
    """Обработка заказа"""
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        telegram = request.POST.get('telegram', '').strip()
        flavor = request.POST.get('flavor', '')
        color = request.POST.get('color', '')
        comment = request.POST.get('comment', '')

        if not telegram:
            messages.error(request, 'Пожалуйста, введите ваш Telegram-ник')
            return redirect('catalog:product_detail', slug=product.slug)

        order = Order.objects.create(
            product=product,
            telegram=telegram,
            flavor=flavor,
            color=color,
            comment=comment
        )

        send_telegram_notification(order, product, flavor, color)

        messages.success(request, f'Спасибо! Ваш заказ на "{product.name}" принят!')
        return redirect('catalog:product_detail', slug=product.slug)

    return redirect('catalog:product_detail', slug=product.slug)


def send_telegram_notification(order, product, flavor, color):
    """Отправка уведомления в Telegram"""
    bot_token = os.getenv('TG_BOT_TOKEN')
    chat_id = os.getenv('TG_CHAT_ID')

    if not bot_token or not chat_id:
        print('❌ Ошибка: TG_BOT_TOKEN или TG_CHAT_ID не заданы в .env')
        return False

    flavor_text = f"\n🍽️ *Вкус:* {flavor}" if flavor else ""
    color_text = f"\n🎨 *Цвет:* {color}" if color else ""
    telegram_link = f"https://t.me/{order.telegram}" if order.telegram else ""

    message = f"""
🛍️ *НОВЫЙ ЗАКАЗ!*

📦 *Товар:* {product.name}
{flavor_text}
{color_text}
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