from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from catalog.models import Product, Category, Order, FlavorStock, ColorStock, BlockedUser
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
    """Список товаров в админке с отображением наличия"""
    try:
        products = Product.objects.all().order_by('-created_at')

        # Добавляем статус наличия для каждого товара
        for product in products:
            product.stock_status = product.get_stock_status()

        return render(request, 'dashboard/products.html', {'products': products})
    except Exception as e:
        import traceback
        error_text = traceback.format_exc()
        print(error_text)
        return HttpResponse(f"<pre>{error_text}</pre>", status=500)

@login_required(login_url='dashboard:login')
@user_passes_test(is_admin, login_url='dashboard:login')
def product_create(request):
    """Создание товара с вкусами, цветами и количеством"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()

            # Добавляем вкусы
            flavors = request.POST.getlist('flavors[]')
            flavors_quantities = request.POST.getlist('flavors_quantities[]')
            for flavor, qty in zip(flavors, flavors_quantities):
                if flavor and qty:
                    try:
                        FlavorStock.objects.create(
                            product=product,
                            flavor=flavor.strip(),
                            quantity=int(qty)
                        )
                    except:
                        pass

            # Добавляем цвета
            colors = request.POST.getlist('colors[]')
            colors_quantities = request.POST.getlist('colors_quantities[]')
            for color, qty in zip(colors, colors_quantities):
                if color and qty:
                    try:
                        ColorStock.objects.create(
                            product=product,
                            color=color.strip(),
                            quantity=int(qty)
                        )
                    except:
                        pass

            messages.success(request, 'Товар успешно создан!')
            return redirect('dashboard:products')
        else:
            messages.error(request, 'Ошибка при создании товара. Проверьте поля.')
    else:
        form = ProductForm()
    return render(request, 'dashboard/product_form.html', {'form': form, 'title': 'Создать товар'})


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin, login_url='dashboard:login')
def product_edit(request, product_id):
    """Редактирование товара с вкусами, цветами и количеством"""
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()

            # Обновляем вкусы
            product.flavor_stocks.all().delete()
            flavors = request.POST.getlist('flavors[]')
            flavors_quantities = request.POST.getlist('flavors_quantities[]')
            for flavor, qty in zip(flavors, flavors_quantities):
                if flavor and qty:
                    try:
                        FlavorStock.objects.create(
                            product=product,
                            flavor=flavor.strip(),
                            quantity=int(qty)
                        )
                    except:
                        pass

            # Обновляем цвета
            product.color_stocks.all().delete()
            colors = request.POST.getlist('colors[]')
            colors_quantities = request.POST.getlist('colors_quantities[]')
            for color, qty in zip(colors, colors_quantities):
                if color and qty:
                    try:
                        ColorStock.objects.create(
                            product=product,
                            color=color.strip(),
                            quantity=int(qty)
                        )
                    except:
                        pass

            messages.success(request, 'Товар обновлен!')
            return redirect('dashboard:products')
        else:
            messages.error(request, 'Ошибка при обновлении товара. Проверьте поля.')
    else:
        form = ProductForm(instance=product)

    return render(request, 'dashboard/product_form.html', {
        'form': form,
        'title': 'Редактировать товар',
        'product': product
    })


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


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin, login_url='dashboard:login')
def blocked_users_list(request):
    """Список заблокированных пользователей"""
    blocked_users = BlockedUser.objects.all().order_by('-blocked_at')
    return render(request, 'dashboard/blocked_users.html', {
        'blocked_users': blocked_users,
        'title': 'Блокировка пользователей'
    })


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin, login_url='dashboard:login')
def blocked_user_create(request):
    """Блокировка пользователя"""
    if request.method == 'POST':
        telegram = request.POST.get('telegram', '').strip()
        reason = request.POST.get('reason', '').strip()

        if telegram:
            # Удаляем @ если есть
            telegram = telegram.lstrip('@')

            # Проверяем, не заблокирован ли уже
            if BlockedUser.objects.filter(telegram=telegram, is_active=True).exists():
                messages.warning(request, f'Пользователь @{telegram} уже заблокирован')
            else:
                # Если был заблокирован ранее, но разблокирован - активируем
                blocked, created = BlockedUser.objects.get_or_create(
                    telegram=telegram,
                    defaults={'reason': reason, 'is_active': True}
                )
                if not created:
                    blocked.is_active = True
                    blocked.reason = reason
                    blocked.save()
                messages.success(request, f'Пользователь @{telegram} заблокирован')
        else:
            messages.error(request, 'Введите Telegram-ник')

        return redirect('dashboard:blocked_users')

    return render(request, 'dashboard/blocked_user_form.html', {
        'title': 'Блокировать пользователя'
    })


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin, login_url='dashboard:login')
def blocked_user_unblock(request, user_id):
    """Разблокировка пользователя"""
    blocked = get_object_or_404(BlockedUser, id=user_id)
    blocked.is_active = False
    blocked.save()
    messages.success(request, f'Пользователь @{blocked.telegram} разблокирован')
    return redirect('dashboard:blocked_users')


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin, login_url='dashboard:login')
def blocked_user_delete(request, user_id):
    """Удаление записи о блокировке"""
    blocked = get_object_or_404(BlockedUser, id=user_id)
    telegram = blocked.telegram
    blocked.delete()
    messages.success(request, f'Запись о блокировке @{telegram} удалена')
    return redirect('dashboard:blocked_users')