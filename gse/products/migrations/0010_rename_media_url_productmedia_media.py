# Generated by Django 5.1 on 2025-01-16 11:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_alter_productcategory_title'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productmedia',
            old_name='media_url',
            new_name='media',
        ),
    ]
