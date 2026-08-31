from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Order, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'in_stock', 'image_preview']
    list_editable = ['price', 'in_stock']
    list_filter = ['category', 'in_stock']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20

    fields = ['name', 'slug', 'category', 'image', 'price', 'in_stock', 'flavors']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;"/>', obj.image.url)
        return 'Нет фото'

    image_preview.short_description = 'Фото'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['telegram_link', 'product', 'flavors', 'created_at']
    list_filter = ['created_at']
    search_fields = ['telegram', 'product__name', 'flavors']
    readonly_fields = ['created_at']
    fields = ['product', 'flavors', 'telegram', 'comment', 'created_at']

    def telegram_link(self, obj):
        if obj.telegram:
            return format_html('<a href="https://t.me/{}" target="_blank">@{}</a>', obj.telegram, obj.telegram)
        return '-'

    telegram_link.short_description = 'Telegram'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['name', 'product', 'rating', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating', 'product']
    search_fields = ['name', 'text', 'telegram']
    list_editable = ['is_approved']
    readonly_fields = ['created_at']