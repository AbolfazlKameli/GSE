# Generated by Django 5.1 on 2024-11-03 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_address_postal_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('admin', 'ادمین'), ('customer', 'مشتری'), ('support', 'پشتیبان')], default='customer', max_length=20, verbose_name='نقش'),
        ),
    ]
