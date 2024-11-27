from datetime import datetime

from django.db import transaction
from pytz import timezone

from .choices import ORDER_STATUS_CANCELLED
from .models import Order, Coupon


def cancel_order(order: Order) -> Order:
    order.status = ORDER_STATUS_CANCELLED
    order.save()
    return order


@transaction.atomic()
def apply_coupon(order: Order, coupon: Coupon) -> Order | None:
    now = datetime.now(tz=timezone('Asia/Tehran'))
    if coupon.expiration_date < now:
        return None

    order.discount_percent = order.discount_percent + coupon.discount_percent
    order.coupon_applied = True
    order.full_clean()
    order.save()
    coupon.max_usage_limit -= 1
    coupon.save()

    return order
