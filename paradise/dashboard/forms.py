from django import forms
from catalog.models import Product, Category


class DashboardProductForm(forms.ModelForm):
    """Форма для управления товарами в админ-панели"""

    class Meta:
        model = Product
        fields = ['category', 'name', 'price', 'image',  'flavors', 'colors']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название товара'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
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
            'flavors': 'Вкусы (каждый с новой строки)',
            'colors': 'Цвета (каждый с новой строки)',
        }


class DashboardCategoryForm(forms.ModelForm):
    """Форма для управления категориями в админ-панели"""

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