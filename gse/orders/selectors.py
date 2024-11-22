from .models import Order, OrderItem


def get_all_orders() -> list[Order]:
    return Order.objects.prefetch_related('items').select_related('owner').all()


def get_all_order_items() -> list[OrderItem]:
    return OrderItem.objects.select_related('product', 'order').all()
