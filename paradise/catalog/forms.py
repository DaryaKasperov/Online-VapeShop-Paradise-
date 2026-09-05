# catalog/forms.py
from django import forms
from .models import Product, Category, Order, Review


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'price', 'image', 'quantity']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название товара'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'min': 0}),
        }
        labels = {
            'category': 'Категория',
            'name': 'Название',
            'price': 'Цена',
            'image': 'Изображение',
            'quantity': 'Количество на складе',
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название категории'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL-адрес (автоматически)',
            }),
        }
        labels = {
            'name': 'Название категории',
            'slug': 'Slug (URL)',
        }
        help_texts = {
            'slug': 'Автоматически генерируется из названия. Можно изменить вручную.',
        }


class OrderForm(forms.ModelForm):
    """Форма для заказа (только Telegram и комментарий)"""

    class Meta:
        model = Order
        # ✅ ТОЛЬКО поля, которые есть в модели Order
        fields = ['telegram', 'comment']
        widgets = {
            'telegram': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ваш_никнейм',
                'required': True,
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Пожелания к заказу...'
            }),
        }
        labels = {
            'telegram': 'Ваш Telegram-ник',
            'comment': 'Комментарий',
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'telegram', 'rating', 'text']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше имя'}),
            'telegram': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваш Telegram-ник (без @)'}),
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Ваш отзыв о товаре...'}),
        }
        labels = {
            'name': 'Ваше имя',
            'telegram': 'Telegram (для связи)',
            'rating': 'Оценка',
            'text': 'Отзыв',
        }