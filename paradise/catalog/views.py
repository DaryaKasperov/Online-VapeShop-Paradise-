from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Category, Product, Order, Flavor, Review
from .filters import ProductFilter
from .forms import ReviewForm, OrderForm  # ← Добавьте OrderForm
import requests
import os


# import re  # ← УДАЛИТЕ re (больше не нужен)


def product_list(request, category_slug=None):
    """Главная страница и список товаров с фильтрацией"""
    categories = Category.objects.all()
    products = Product.objects.filter(in_stock=True).prefetch_related('flavors', 'reviews')

    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    filter = ProductFilter(request.GET, queryset=products)
    products = filter.qs

    context = {
        'categories': categories,
        'category': category,
        'filter': filter,
        'products': products,
    }
    return render(request, 'catalog/product_list.html', context)


def product_detail(request, slug):
    """Страница одного товара с отзывами"""
    product = get_object_or_404(Product, slug=slug, in_stock=True)
    flavors = product.flavors.filter(is_active=True)
    reviews = product.reviews.filter(is_approved=True).order_by('-created_at')

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
        'reviews': reviews,
        'review_form': form,
    }
    return render(request, 'catalog/product_detail.html', context)


def order_create(request, product_id):
    """Обработка заказа через ModelForm"""
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # Создаем форму с данными из POST
        form = OrderForm(request.POST)

        # Валидация происходит в форме (clean_telegram)
        if form.is_valid():
            # Получаем данные из формы
            telegram = form.cleaned_data['telegram']
            comment = form.cleaned_data['comment']
            flavor_id = request.POST.get('flavor')

            # Получаем выбранный вкус
            flavor = None
            if flavor_id:
                flavor = get_object_or_404(Flavor, id=flavor_id)

            # Создаем заказ
            order = Order.objects.create(
                product=product,
                flavor=flavor,
                telegram=telegram,  # Уже очищенный и валидный
                comment=comment
            )

            send_telegram_notification(order, product, flavor)

            messages.success(request, f'Спасибо! Ваш заказ на "{product.name}" принят!')
            return redirect('catalog:product_detail', slug=product.slug)
        else:
            # Если форма не валидна — показываем ошибки
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
            return redirect('catalog:product_detail', slug=product.slug)

    return redirect('catalog:product_detail', slug=product.slug)


def send_telegram_notification(order, product, flavor):
    """Отправка уведомления в Telegram"""
    bot_token = os.getenv('TG_BOT_TOKEN')
    chat_id = os.getenv('TG_CHAT_ID')

    if not bot_token or not chat_id:
        print('❌ Ошибка: TG_BOT_TOKEN или TG_CHAT_ID не заданы в .env')
        return False

    flavor_text = f"\n🍽️ *Вкус:* {flavor.name}" if flavor else ""
    telegram_link = f"https://t.me/{order.telegram}" if order.telegram else ""

    message = f"""
🛍️ *НОВЫЙ ЗАКАЗ!*

📦 *Товар:* {product.name}
{flavor_text}
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