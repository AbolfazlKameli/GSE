from .models import Order


def get_all_orders() -> list[Order]:
    return Order.objects.prefetch_related('items').select_related('owner').all()
