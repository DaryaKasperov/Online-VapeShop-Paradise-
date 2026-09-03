from django.db import models
from django.conf import settings
from catalog.models import Product, FlavorStock, ColorStock

class CartItem(models.Model):
    """Модель для товара в корзине"""
    session_key = models.CharField('Ключ сессии', max_length=40)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    flavor = models.CharField('Вкус', max_length=100, blank=True)
    color = models.CharField('Цвет', max_length=100, blank=True)
    quantity = models.PositiveIntegerField('Количество', default=1)
    created_at = models.DateTimeField('Добавлен', auto_now_add=True)

    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'

    def get_total_price(self):
        """Общая цена за этот товар"""
        return self.product.price * self.quantity

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'