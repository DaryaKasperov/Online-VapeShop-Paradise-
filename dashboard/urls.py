# dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Вход и выход
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),

    # Главная
    path('', views.dashboard_index, name='index'),

    # Товары
    path('products/', views.product_list_admin, name='products'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/edit/<int:product_id>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:product_id>/', views.product_delete, name='product_delete'),

    # Категории
    path('categories/', views.category_list_admin, name='categories'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/edit/<int:category_id>/', views.category_edit, name='category_edit'),
    path('categories/delete/<int:category_id>/', views.category_delete, name='category_delete'),

    # Заказы
    path('orders/', views.orders_list, name='orders'),

    # Блокировка пользователей
    path('blocked/', views.blocked_users_list, name='blocked_users'),
    path('blocked/create/', views.blocked_user_create, name='blocked_user_create'),
    path('blocked/unblock/<int:user_id>/', views.blocked_user_unblock, name='blocked_user_unblock'),
    path('blocked/delete/<int:user_id>/', views.blocked_user_delete, name='blocked_user_delete'),
]