# Generated by Django 5.1 on 2024-11-30 19:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orders', '0013_remove_order_coupon_applied'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('authority_id', models.CharField(max_length=250)),
                ('ref_id', models.CharField(max_length=250)),
                ('amount', models.DecimalField(decimal_places=0, max_digits=15)),
                ('response_json', models.JSONField()),
                ('response_code', models.IntegerField()),
                ('status', models.CharField(choices=[('pending', 'پرداخت نشده'), ('success', 'پرداخت شده'), ('failed', 'ناموفق')], default='pending', max_length=10, verbose_name='وضعیت پرداخت')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='orders.order')),
            ],
        ),
    ]
