from .choices import ORDER_STATUS_CANCELLED
from .models import Order


def cancel_order(order: Order) -> Order:
    order.status = ORDER_STATUS_CANCELLED
    order.save()
    return order
