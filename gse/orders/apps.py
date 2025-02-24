from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gse.orders'

    def ready(self):
        import gse.orders.signals
