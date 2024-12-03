from datetime import datetime

from pytz import timezone

from gse.users.models import User
from gse.users.selectors import get_admins_and_supporters_ids
from .choices import ORDER_STATUS_PENDING
from .models import Order, OrderItem, Coupon


def get_all_orders() -> list[Order]:
    return Order.objects.prefetch_related('items').select_related('owner').all()


def get_all_order_items() -> list[OrderItem]:
    return OrderItem.objects.select_related('product', 'order').all()


def get_pending_orders() -> list[Order]:
    return Order.objects.filter(status=ORDER_STATUS_PENDING).all()


def get_order_by_id(order_id: int, check_owner: bool, owner: User = None) -> Order | None:
    allowed_users: list[int] = get_admins_and_supporters_ids()
    if check_owner and owner:
        allowed_users.append(owner.id)
        return Order.objects.filter(id=order_id, owner__in=allowed_users).first()
    return Order.objects.filter(id=order_id).first()


def check_order_status(order: Order, statuses: list) -> bool:
    return order.status in statuses


def get_all_coupons() -> list[Coupon]:
    return Coupon.objects.all()


def get_coupon_by_id(coupon_id: int) -> Coupon | None:
    return Coupon.objects.filter(id=coupon_id).first()


def get_coupon_by_code(code: str) -> Coupon | None:
    return Coupon.objects.filter(code__exact=code).first()


def get_usable_coupon_by_code(coupon_code: str) -> Coupon | None:
    now = datetime.now(tz=timezone('Asia/Tehran'))
    return Coupon.objects.filter(code__exact=coupon_code, expiration_date__gt=now, max_usage_limit__gt=0).first()


def get_invalid_coupons() -> list[Coupon]:
    now = datetime.now(tz=timezone('Asia/Tehran'))
    return Coupon.objects.filter(expiration_date__lt=now)
