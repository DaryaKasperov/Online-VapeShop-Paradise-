from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_view, name='cart_view'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('update/<int:item_id>/', views.cart_update, name='cart_update'),
    path('checkout/', views.cart_checkout, name='cart_checkout'),
    path('clear/', views.cart_clear, name='cart_clear'),
]