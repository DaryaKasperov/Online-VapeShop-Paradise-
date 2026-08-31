from django.db import migrations
from django.utils.text import slugify

def fix_empty_slugs(apps, schema_editor):
    Product = apps.get_model('catalog', 'Product')
    for product in Product.objects.all():
        if not product.slug:
            product.slug = slugify(product.name)
            # Проверяем уникальность
            if Product.objects.filter(slug=product.slug).exclude(id=product.id).exists():
                product.slug = f"{product.slug}-{product.id}"
            product.save()

class Migration(migrations.Migration):
    dependencies = [
        ('catalog', 'предыдущая_миграция'),  # Замените на последнюю миграцию
    ]

    operations = [
        migrations.RunPython(fix_empty_slugs),
    ]