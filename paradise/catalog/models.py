from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:category', args=[self.slug])


class Flavor(models.Model):
    name = models.CharField('Название вкуса', max_length=100)
    price_extra = models.DecimalField('Доплата', max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Вкус'
        verbose_name_plural = 'Вкусы'

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='products', verbose_name='Категория')
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField('Изображение', upload_to='products/', blank=True, null=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    in_stock = models.BooleanField('В наличии', default=True)
    flavors = models.ManyToManyField(Flavor, blank=True, verbose_name='Доступные вкусы')
    created_at = models.DateTimeField('Добавлен', auto_now_add=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug or self.slug == '':
            self.slug = slugify(self.name)
            # Если такой slug уже есть, добавляем ID
            if Product.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                import time
                self.slug = f"{self.slug}-{int(time.time())}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:product_detail', args=[self.slug])


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    flavor = models.ForeignKey(Flavor, on_delete=models.SET_NULL, null=True, blank=True,
                               verbose_name='Выбранный вкус')
    telegram = models.CharField(
        'Telegram',
        max_length=100,
        help_text='Введите ваш Telegram-ник без @'  # Валидация в forms.py
    )
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