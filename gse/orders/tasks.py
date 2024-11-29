from celery import shared_task

from gse.orders.models import Order
from gse.orders.selectors import get_invalid_coupons
from gse.orders.services import discard_coupon


@shared_task
def discard_expired_coupons() -> list[int]:
    invalid_coupons = get_invalid_coupons()
    if invalid_coupons:
        orders = Order.objects.filter(coupon__in=invalid_coupons).select_related('coupon')
        affected_orders = [discard_coupon(order, order.coupon).id for order in orders]
        return affected_orders
