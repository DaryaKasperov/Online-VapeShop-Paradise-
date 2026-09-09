import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    # Поиск по названию товара
    search = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label='Поиск по названию')

    class Meta:
        model = Product
        fields = ['category', 'search']