from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_promocode_alter_colorstock_options_and_more'),
    ]

    operations = [
        # Добавляем колонку status
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'В обработке'),
                    ('confirmed', 'Подтвержден'),
                    ('shipped', 'Отправлен'),
                    ('delivered', 'Доставлен'),
                    ('cancelled', 'Отменен'),
                ],
                default='pending',
                max_length=20,
                verbose_name='Статус',
            ),
        ),
        # Добавляем колонку total_price
        migrations.AddField(
            model_name='order',
            name='total_price',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                verbose_name='Итого',
            ),
        ),
    ]