# Generated by Django 5.1 on 2024-11-21 14:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0005_alter_cart_options_alter_cartitem_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cart',
            old_name='update_date',
            new_name='updated_date',
        ),
        migrations.RenameField(
            model_name='cartitem',
            old_name='update_date',
            new_name='updated_date',
        ),
    ]
