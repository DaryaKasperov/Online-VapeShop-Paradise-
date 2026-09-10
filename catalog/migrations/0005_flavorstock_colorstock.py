from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_category_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='FlavorStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flavor', models.CharField(max_length=100)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('product', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='flavor_stocks',
                    to='catalog.product',
                )),
            ],
        ),
        migrations.CreateModel(
            name='ColorStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(max_length=100)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('product', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='color_stocks',
                    to='catalog.product',
                )),
            ],
        ),
    ]