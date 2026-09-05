from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
path('product/<slug:slug>/review/', views.add_review, name='add_review'),
    path('', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='category'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    ]

