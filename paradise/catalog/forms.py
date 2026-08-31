from django import forms
from .models import Product, Category, Order, Review


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'price', 'image', 'in_stock', 'flavors', 'colors']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название товара'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'in_stock': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'flavors': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Введите каждый вкус с новой строки\nНапример:\nКлубника\nШоколад\nВаниль'
            }),
            'colors': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Введите каждый цвет с новой строки\nНапример:\nЧерный\nБелый\nКрасный'
            }),
        }
        labels = {
            'category': 'Категория',
            'name': 'Название',
            'price': 'Цена',
            'image': 'Изображение',
            'in_stock': 'В наличии',
            'flavors': 'Вкусы (каждый с новой строки)',
            'colors': 'Цвета (каждый с новой строки)',
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
    class Meta:
        model = Order
        fields = ['telegram', 'flavor', 'color', 'comment']
        widgets = {
            'telegram': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ваш_никнейм',
                'required': True,
            }),
            'flavor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Выберите вкус из списка',
                'readonly': True,
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Выберите цвет из списка',
                'readonly': True,
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Пожелания к заказу...'
            }),
        }
        labels = {
            'telegram': 'Ваш Telegram-ник',
            'flavor': 'Выбранный вкус',
            'color': 'Выбранный цвет',
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