# dashboard/forms.py
from django import forms
from catalog.models import Product, Category, FlavorStock, ColorStock


class DashboardProductForm(forms.ModelForm):
    """Форма для управления товарами в админ-панели"""

    # Кастомные поля для вкусов и цветов (НЕ из модели Product)
    flavors = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Вкус:количество (каждый с новой строки)\nНапример:\nКлубника:10\nШоколад:15'
        }),
        label='Вкусы и количество',
        help_text='Формат: Название:Количество'
    )

    colors = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Цвет:количество (каждый с новой строки)\nНапример:\nКрасный:5\nСиний:8'
        }),
        label='Цвета и количество',
        help_text='Формат: Название:Количество'
    )

    class Meta:
        model = Product
        fields = ['category', 'name', 'price', 'image', 'quantity', 'in_stock']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название товара'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'min': 0}),
            'in_stock': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'category': 'Категория',
            'name': 'Название',
            'price': 'Цена',
            'image': 'Изображение',
            'quantity': 'Количество на складе',
        'in_stock': 'В наличии',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Если редактируем товар, заполняем поля вкусов и цветов
        if self.instance and self.instance.pk:
            flavors_text = '\n'.join([
                f'{fs.flavor}:{fs.quantity}'
                for fs in self.instance.flavor_stocks.all()
            ])
            colors_text = '\n'.join([
                f'{cs.color}:{cs.quantity}'
                for cs in self.instance.color_stocks.all()
            ])
            self.initial['flavors'] = flavors_text
            self.initial['colors'] = colors_text

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()

            # Обработка вкусов
            flavors_data = self.cleaned_data.get('flavors', '')
            if flavors_data:
                instance.flavor_stocks.all().delete()
                for line in flavors_data.split('\n'):
                    if ':' in line:
                        name, quantity = line.split(':', 1)
                        try:
                            quantity = int(quantity.strip())
                            if quantity > 0:
                                FlavorStock.objects.create(
                                    product=instance,
                                    flavor=name.strip(),
                                    quantity=quantity
                                )
                        except ValueError:
                            pass

            # Обработка цветов
            colors_data = self.cleaned_data.get('colors', '')
            if colors_data:
                instance.color_stocks.all().delete()
                for line in colors_data.split('\n'):
                    if ':' in line:
                        name, quantity = line.split(':', 1)
                        try:
                            quantity = int(quantity.strip())
                            if quantity > 0:
                                ColorStock.objects.create(
                                    product=instance,
                                    color=name.strip(),
                                    quantity=quantity
                                )
                        except ValueError:
                            pass

            # Обновляем статус наличия
            instance.in_stock = instance.has_stock()
            instance.save()

        return instance