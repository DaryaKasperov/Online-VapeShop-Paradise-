from django.db import models
from django.urls import reverse
from django.utils.text import slugify
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
        """Транслитерация русского текста в латиницу"""
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

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:category', args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='products', verbose_name='Категория')
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField('Изображение', upload_to='products/', blank=True, null=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    in_stock = models.BooleanField('В наличии', default=True)
    flavors = models.TextField('Вкусы', blank=True, default='', help_text='Введите каждый вкус с новой строки')
    colors = models.TextField('Цвета', blank=True, default='', help_text='Введите каждый цвет с новой строки')
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
        """Транслитерация русского текста в латиницу"""
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

        import re
        result = result.lower()
        result = re.sub(r'[^a-z0-9\s-]', '', result)
        result = re.sub(r'[\s_-]+', '-', result)
        result = re.sub(r'^-+|-+$', '', result)
        return result

    def get_flavors_list(self):
        """Возвращает список вкусов из текстового поля"""
        if self.flavors:
            return [f.strip() for f in self.flavors.split('\n') if f.strip()]
        return []

    def get_colors_list(self):
        """Возвращает список цветов из текстового поля"""
        if self.colors:
            return [c.strip() for c in self.colors.split('\n') if c.strip()]
        return []

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:product_detail', args=[self.slug])
class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    flavor = models.CharField('Выбранный вкус', max_length=100, blank=True)
    color = models.CharField('Выбранный цвет', max_length=100, blank=True)
    telegram = models.CharField('Telegram', max_length=100)
    comment = models.TextField('Комментарий', blank=True)
    created_at = models.DateTimeField('Дата заказа', auto_now_add=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ от @{self.telegram} на {self.product.name}'

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