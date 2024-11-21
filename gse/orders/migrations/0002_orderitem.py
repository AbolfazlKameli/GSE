# Generated by Django 5.1 on 2024-11-21 11:56

import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
        ('products', '0004_alter_product_slug_alter_productcategory_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_price', models.DecimalField(decimal_places=0, default=0, max_digits=15, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('quantity', models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(100)])),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_data', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='products.product')),
            ],
        ),
    ]
