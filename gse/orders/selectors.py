from datetime import datetime

from pytz import timezone

from gse.products.models import Product
from gse.users.choices import USER_ROLE_ADMIN, USER_ROLE_SUPPORT
from gse.users.models import User
from .choices import ORDER_STATUS_SUCCESS, ORDER_STATUS_PENDING
from .models import Order, Coupon


def get_all_orders() -> list[Order]:
    return Order.objects.prefetch_related('items').select_related('owner', 'coupon').all()


def get_pending_orders() -> list[Order]:
    return Order.objects.filter(status=ORDER_STATUS_PENDING).select_related('owner').all()


def get_order_by_id(order_id: int) -> Order | None:
    return Order.objects.filter(id=order_id) \
        .prefetch_related('items', 'payment') \
        .select_related('owner', 'coupon') \
        .first()


def check_order_owner(order: Order) -> bool:
    return order.owner.role not in [USER_ROLE_ADMIN, USER_ROLE_SUPPORT]


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


def has_purchased(user: User, product: Product):
    return Order.objects.filter(owner=user, items__product=product, status=ORDER_STATUS_SUCCESS).exists()
