from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Вход и выход
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),

    # Основные страницы
    path('', views.dashboard_index, name='index'),
    path('products/', views.product_list_admin, name='products'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/edit/<int:product_id>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:product_id>/', views.product_delete, name='product_delete'),
    path('orders/', views.orders_list, name='orders'),

    # Вкусы (добавьте эти строки)
    path('flavors/', views.flavor_list_admin, name='flavors'),
    path('flavors/create/', views.flavor_create, name='flavor_create'),
    path('flavors/edit/<int:flavor_id>/', views.flavor_edit, name='flavor_edit'),
    path('flavors/delete/<int:flavor_id>/', views.flavor_delete, name='flavor_delete'),
]