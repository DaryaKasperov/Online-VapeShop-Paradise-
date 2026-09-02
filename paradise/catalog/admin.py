from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Order, Review, FlavorStock, ColorStock


class FlavorStockInline(admin.TabularInline):
    model = FlavorStock
    extra = 1
    fields = ['flavor', 'quantity']
    verbose_name = 'Вкус'
    verbose_name_plural = 'Вкусы и остатки'


class ColorStockInline(admin.TabularInline):
    model = ColorStock
    extra = 1
    fields = ['color', 'quantity']
    verbose_name = 'Цвет'
    verbose_name_plural = 'Цвета и остатки'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'quantity', 'in_stock', 'image_preview']
    list_editable = ['price', 'quantity', 'in_stock']
    list_filter = ['category', 'in_stock']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20

    inlines = [FlavorStockInline, ColorStockInline]

    fields = ['name', 'slug', 'category', 'image', 'price', 'quantity', 'in_stock']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;"/>', obj.image.url)
        return 'Нет фото'

    image_preview.short_description = 'Фото'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'flavor', 'color', 'quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['telegram', 'product__name', 'flavor', 'color']
    readonly_fields = ['created_at']
    fields = ['product', 'flavor', 'color', 'quantity', 'telegram', 'comment', 'created_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['name', 'product', 'rating', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating', 'product']
    search_fields = ['name', 'text', 'telegram']
    list_editable = ['is_approved']
    readonly_fields = ['created_at']