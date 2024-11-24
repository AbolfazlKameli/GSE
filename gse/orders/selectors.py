from .models import Order, OrderItem


def get_all_orders() -> list[Order]:
    return Order.objects.prefetch_related('items').select_related('owner').all()


def get_all_order_items() -> list[OrderItem]:
    return OrderItem.objects.select_related('product', 'order').all()


def get_order_by_id(order_id: int) -> Order | None:
    return Order.objects.filter(id=order_id).first()


def check_order_status(order: Order, statuses: list) -> bool:
    return order.status in statuses
