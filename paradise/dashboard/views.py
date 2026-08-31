from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from catalog.models import Product, Category, Order
from catalog.forms import ProductForm, CategoryForm


# Проверка, что пользователь админ
def is_admin(user):
    return user.is_staff or user.is_superuser


# ========== СТРАНИЦА ВХОДА ==========
def admin_login(request):
    """Страница входа в админ-панель"""
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('dashboard:index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and is_admin(user):
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('dashboard:index')
        elif user is not None:
            messages.error(request, 'У вас нет прав доступа к админ-панели.')
        else:
            messages.error(request, 'Неверный логин или пароль.')

    return render(request, 'dashboard/login.html')


# ========== ВЫХОД ==========
def admin_logout(request):
    """Выход из админ-панели"""
    logout(request)
    messages.info(request, 'Вы вышли из админ-панели.')
    return redirect('dashboard:login')


# ========== ГЛАВНАЯ АДМИНКИ ==========
@login_required(login_url='dashboard:login')
@user_passes_test(is_admin, login_url='dashboard:login')
def dashboard_index(request):
    """Главная страница админ-панели"""
    context = {
        'products_count': Product.objects.count(),
        'categories_count': Category.objects.count(),
        'orders_count': Order.objects.count(),
    }
    return render(request, 'dashboard/index.html', context)


# ========== ТОВАРЫ ==========
@login_required(login_url='dashboard:login')
@user_passes_test(is_admin, login_url='dashboard:login')
def product_list_admin(request):
    """Список товаров в админке"""
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'dashboard/products.html', {'products': products})


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin, login_url='dashboard:login')
def product_create(request):
    """Создание товара"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар успешно создан!')
            return redirect('dashboard:products')
    else:
        form = ProductForm()
    return render(request, 'dashboard/product_form.html', {'form': form, 'title': 'Создать товар'})


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin, login_url='dashboard:login')
def product_edit(request, product_id):
    """Редактирование товара"""
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар обновлен!')
            return redirect('dashboard:products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'dashboard/product_form.html', {'form': form, 'title': 'Редактировать товар'})


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin, login_url='dashboard:login')
def product_delete(request, product_id):
    """Удаление товара"""
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Товар удален!')
        return redirect('dashboard:products')
    return render(request, 'dashboard/product_confirm_delete.html', {'product': product})


# ========== ЗАКАЗЫ ==========
@login_required(login_url='dashboard:login')
@user_passes_test(is_admin, login_url='dashboard:login')
def orders_list(request):
    """Список заказов"""
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'dashboard/orders.html', {'orders': orders})

# ========== КАТЕГОРИИ ==========
@login_required(login_url='dashboard:login')
@user_passes_test(is_admin, login_url='dashboard:login')
def category_list_admin(request):
    """Список категорий в админке"""
    categories = Category.objects.all().order_by('name')
    return render(request, 'dashboard/category_manage.html', {
        'categories': categories,
        'action': 'list'
    })


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin, login_url='dashboard:login')
def category_create(request):
    """Создание категории"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория успешно создана!')
            return redirect('dashboard:categories')
    else:
        form = CategoryForm()
    return render(request, 'dashboard/category_manage.html', {
        'form': form,
        'title': 'Создать категорию',
        'action': 'form'
    })


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin, login_url='dashboard:login')
def category_edit(request, category_id):
    """Редактирование категории"""
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория обновлена!')
            return redirect('dashboard:categories')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'dashboard/category_manage.html', {
        'form': form,
        'title': 'Редактировать категорию',
        'action': 'form'
    })


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin, login_url='dashboard:login')
def category_delete(request, category_id):
    """Удаление категории"""
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Категория удалена!')
        return redirect('dashboard:categories')
    return render(request, 'dashboard/category_manage.html', {
        'category': category,
        'action': 'delete'
    })