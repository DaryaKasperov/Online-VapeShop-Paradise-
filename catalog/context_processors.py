# catalog/context_processors.py
from .models import Category

def categories(request):
    """Контекстный процессор для передачи категорий во все шаблоны"""
    return {
        'categories': Category.objects.filter(is_active=True)
    }