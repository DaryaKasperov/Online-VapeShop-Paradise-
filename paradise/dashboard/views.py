from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from catalog.models import Product, Category, Flavor, Order
from catalog.forms import ProductForm, CategoryForm, FlavorForm


# Проверка, что пользователь админ
def is_admin(user):
    return user.is_staff or user.is_superuser


# ========== СТРАНИЦА ВХОДА ==========
def admin_login(request):
    """Страница входа в админ-панель"""
    # Если пользователь уже авторизован - перенаправляем в админку
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
        'flavors_count': Flavor.objects.count(),
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


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin, login_url='dashboard:login')
def orders_list(request):
    """Список заказов"""
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'dashboard/orders.html', {'orders': orders})

# Добавьте эти функции в dashboard/views.py

@login_required(login_url='dashboard:login')
@user_passes_test(is_admin, login_url='dashboard:login')
def flavor_list_admin(request):
    """Список вкусов в админке"""
    flavors = Flavor.objects.all().order_by('name')
    return render(request, 'dashboard/flavors.html', {'flavors': flavors})

@login_required(login_url='dashboard:login')
@user_passes_test(is_admin, login_url='dashboard:login')
def flavor_create(request):
    """Создание вкуса"""
    if request.method == 'POST':
        form = FlavorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Вкус успешно создан!')
            return redirect('dashboard:flavors')
    else:
        form = FlavorForm()
    return render(request, 'dashboard/flavor_form.html', {'form': form, 'title': 'Создать вкус'})

@login_required(login_url='dashboard:login')
@user_passes_test(is_admin, login_url='dashboard:login')
def flavor_edit(request, flavor_id):
    """Редактирование вкуса"""
    flavor = get_object_or_404(Flavor, id=flavor_id)
    if request.method == 'POST':
        form = FlavorForm(request.POST, instance=flavor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Вкус обновлен!')
            return redirect('dashboard:flavors')
    else:
        form = FlavorForm(instance=flavor)
    return render(request, 'dashboard/flavor_form.html', {'form': form, 'title': 'Редактировать вкус'})

@login_required(login_url='dashboard:login')
@user_passes_test(is_admin, login_url='dashboard:login')
def flavor_delete(request, flavor_id):
    """Удаление вкуса"""
    flavor = get_object_or_404(Flavor, id=flavor_id)
    if request.method == 'POST':
        flavor.delete()
        messages.success(request, 'Вкус удален!')
        return redirect('dashboard:flavors')
    return render(request, 'dashboard/flavor_confirm_delete.html', {'flavor': flavor})

