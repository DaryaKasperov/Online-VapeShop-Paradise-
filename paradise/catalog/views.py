from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import Category, Product, Order, Review, FlavorStock, ColorStock
from .filters import ProductFilter
from .forms import ReviewForm, OrderForm
import requests
import os

# catalog/views.py
from django.shortcuts import render, get_object_or_404
from .models import Category, Product


def product_list(request, category_slug=None):
    """Главная страница и список товаров с фильтрацией"""
    categories = Category.objects.all()

    # ✅ Получаем ВСЕ товары (не только in_stock=True)
    products = Product.objects.all()

    # ✅ Оставляем только те, у которых есть наличие (через has_stock)
    filtered_products = []
    for product in products:
        if product.has_stock():  # Проверяет вкусы, цвета и quantity
            filtered_products.append(product.id)

    products = products.filter(id__in=filtered_products)

    # Переменная для заголовка
    page_title = 'Все товары'
    category = None

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
        page_title = category.name

    # Фильтр по категории из GET
    category_id = request.GET.get('category')
    if category_id and not category:
        try:
            category = Category.objects.get(id=category_id)
            products = products.filter(category=category)
        except Category.DoesNotExist:
            pass

    # Поиск
    search = request.GET.get('search')
    if search:
        products = products.filter(name__icontains=search)

    context = {
        'categories': categories,
        'category': category,
        'products': products,
        'page_title': page_title,
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
        }
        return render(request, 'catalog/product_detail.html', context)
    except Exception as e:
        import traceback
        error_text = traceback.format_exc()
        print(error_text)
        return HttpResponse(f"<pre>{error_text}</pre>", status=500)


def add_review(request, slug):
    """Добавление отзыва к товару"""
    product = get_object_or_404(Product, slug=slug)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.is_approved = True  # или False для модерации
            review.save()
            messages.success(request, 'Спасибо за ваш отзыв!')
            return redirect('catalog:product_detail', slug=product.slug)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')

    return redirect('catalog:product_detail', slug=product.slug)

