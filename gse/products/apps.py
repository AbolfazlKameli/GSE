from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gse.products'

    def ready(self):
        from .signals import delete_media_files
