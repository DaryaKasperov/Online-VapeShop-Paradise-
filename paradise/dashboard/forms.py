from django import forms
from .models import Product, Category, Flavor, Review

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'price', 'image', 'in_stock', 'flavors']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название товара'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'in_stock': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'flavors': forms.SelectMultiple(attrs={'class': 'form-control', 'style': 'height: 120px;'}),
        }
        labels = {
            'category': 'Категория',
            'name': 'Название',
            'price': 'Цена',
            'image': 'Изображение',
            'in_stock': 'В наличии',
            'flavors': 'Доступные вкусы',
        }



class FlavorForm(forms.ModelForm):
    class Meta:
        model = Flavor
        fields = ['name', 'price_extra', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название вкуса'}),
            'price_extra': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Название вкуса',
            'price_extra': 'Доплата',
            'is_active': 'Активен',
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