from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Order, OrderItem, Review, FlavorStock, ColorStock


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


class OrderItemInline(admin.TabularInline):
    """Позиции заказа в админке"""
    model = OrderItem
    extra = 0
    fields = ['product', 'quantity', 'price']  # ✅ УБРАЛ flavor, color (они в OrderItem)
    readonly_fields = ['price']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'telegram', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['id', 'telegram', 'comment']
    readonly_fields = ['created_at', 'total_price']
    inlines = [OrderItemInline]

    fields = ['telegram', 'comment', 'status', 'total_price', 'created_at']  # ✅ ТОЛЬКО поля из Order

    actions = ['mark_as_confirmed', 'mark_as_shipped', 'mark_as_delivered']

    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} заказов подтверждены')
    mark_as_confirmed.short_description = 'Подтвердить заказы'

    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} заказов отправлены')
    mark_as_shipped.short_description = 'Отправить заказы'

    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} заказов доставлены')
    mark_as_delivered.short_description = 'Доставить заказы'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']  # ✅ flavor, color убраны
    list_filter = ['order__status']
    search_fields = ['product__name', 'order__id']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['name', 'product', 'rating', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating', 'product']
    search_fields = ['name', 'text', 'telegram']
    list_editable = ['is_approved']
    readonly_fields = ['created_at']


@admin.register(FlavorStock)
class FlavorStockAdmin(admin.ModelAdmin):
    list_display = ['product', 'flavor', 'quantity']
    list_filter = ['product__category']
    search_fields = ['flavor', 'product__name']


@admin.register(ColorStock)
class ColorStockAdmin(admin.ModelAdmin):
    list_display = ['product', 'color', 'quantity']
    list_filter = ['product__category']
    search_fields = ['color', 'product__name']