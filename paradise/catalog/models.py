from django.db import models
from django.urls import reverse
import re


class Category(models.Model):
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.transliterate(self.name)
            counter = 1
            while Category.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{self.transliterate(self.name)}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def transliterate(self, text):
        map = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
            'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
            'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
            'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
            'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
        }
        result = ''
        for char in text:
            result += map.get(char, char)
        result = result.lower()
        result = re.sub(r'[^a-z0-9\s-]', '', result)
        result = re.sub(r'[\s_-]+', '-', result)
        result = re.sub(r'^-+|-+$', '', result)
        return result

    pass

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:category', args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='product', verbose_name='Категория')
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField('Изображение', upload_to='product/', blank=True, null=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    in_stock = models.BooleanField('В наличии', default=True)
    quantity = models.PositiveIntegerField('Количество на складе', default=0)
    created_at = models.DateTimeField('Добавлен', auto_now_add=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug or self.slug == '':
            self.slug = self.transliterate(self.name)
            if not self.slug:
                import time
                self.slug = f"product-{int(time.time())}"
            counter = 1
            while Product.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{self.transliterate(self.name)}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def transliterate(self, text):
        map = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
            'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
            'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
            'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
            'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
        }
        result = ''
        for char in text:
            result += map.get(char, char)
        result = result.lower()
        result = re.sub(r'[^a-z0-9\s-]', '', result)
        result = re.sub(r'[\s_-]+', '-', result)
        result = re.sub(r'^-+|-+$', '', result)
        return result

    def has_stock(self):
        """Проверяет, есть ли у товара наличие"""
        if self.quantity > 0:
            return True
        if self.flavor_stocks.filter(quantity__gt=0).exists():
            return True
        if self.color_stocks.filter(quantity__gt=0).exists():
            return True
        return False

    def get_stock_status(self):
        """Возвращает статус наличия для отображения"""
        if self.has_stock():
            return 'В наличии'
        return 'Нет в наличии'

    def get_flavors_with_stock(self):
        """Возвращает список вкусов с остатками"""
        return self.flavor_stocks.filter(quantity__gt=0).order_by('flavor')

    def get_colors_with_stock(self):
        """Возвращает список цветов с остатками"""
        return self.color_stocks.filter(quantity__gt=0).order_by('color')

    def get_total_quantity(self):
        """Общее количество всех вкусов и цветов"""
        total = sum(fs.quantity for fs in self.flavor_stocks.all())
        total += sum(cs.quantity for cs in self.color_stocks.all())
        return total

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:product_detail', args=[self.slug])


# ========== ОСТАТКИ ВКУСОВ ==========
class FlavorStock(models.Model):
    """Модель для хранения количества по каждому вкусу"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                               related_name='flavor_stocks', verbose_name='Товар')
    flavor = models.CharField('Название вкуса', max_length=100)
    quantity = models.PositiveIntegerField('Количество на складе', default=0)

    class Meta:
        verbose_name = 'Остаток вкуса'
        verbose_name_plural = 'Остатки вкусов'
        unique_together = ['product', 'flavor']

    def __str__(self):
        return f'{self.product.name} - {self.flavor}: {self.quantity} шт.'


# ========== ОСТАТКИ ЦВЕТОВ ==========
class ColorStock(models.Model):
    """Модель для хранения количества по каждому цвету"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                               related_name='color_stocks', verbose_name='Товар')
    color = models.CharField('Название цвета', max_length=100)
    quantity = models.PositiveIntegerField('Количество на складе', default=0)

    class Meta:
        verbose_name = 'Остаток цвета'
        verbose_name_plural = 'Остатки цветов'
        unique_together = ['product', 'color']

    def __str__(self):
        return f'{self.product.name} - {self.color}: {self.quantity} шт.'


# ========== ЗАКАЗ ==========

class Order(models.Model):
    """Модель заказа"""
    STATUS_CHOICES = [
        ('pending', 'В обработке'),
        ('confirmed', 'Подтвержден'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]

    telegram = models.CharField('Telegram', max_length=100)
    comment = models.TextField('Комментарий', blank=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField('Итого', max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField('Дата заказа', auto_now_add=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.id} от @{self.telegram}'


class OrderItem(models.Model):
    """Модель позиции в заказе"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    flavor = models.CharField('Вкус', max_length=100, blank=True)
    color = models.CharField('Цвет', max_length=100, blank=True)
    quantity = models.PositiveIntegerField('Количество', default=1)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'
# ========== ОТЗЫВ ==========
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='reviews', verbose_name='Товар')
    name = models.CharField('Имя', max_length=100)
    telegram = models.CharField('Telegram', max_length=100, blank=True)
    text = models.TextField('Текст отзыва')
    rating = models.PositiveIntegerField('Оценка', choices=[
        (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')
    ], default=5)
    is_approved = models.BooleanField('Одобрен', default=True)
    created_at = models.DateTimeField('Дата отзыва', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.product.name}'