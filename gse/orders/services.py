from datetime import datetime

from django.db import transaction
from pytz import timezone

from gse.cart.models import Cart, CartItem
from gse.products.models import Product
from gse.users.models import User
from .choices import ORDER_STATUS_CANCELLED
from .models import Order, Coupon, OrderItem


@transaction.atomic()
def create_order(owner: User, items: list[dict[str, int | Product]]) -> Order:
    cart = Cart.objects.select_related('owner').prefetch_related('items__product').get(owner=owner)

    products_to_update = []
    cart_items_to_delete = []
    order_items = []

    for item in items:
        product = item.get('product')
        quantity = item.get('quantity')

        product.quantity -= quantity
        products_to_update.append(product)

        cart_item = cart.items.filter(product=product, quantity=quantity).first()
        if cart_item:
            cart_items_to_delete.append(cart_item)

        order_items.append(OrderItem(order=None, product=product, quantity=quantity))

    Product.objects.bulk_update(products_to_update, ['quantity'])
    CartItem.objects.filter(id__in=[item.id for item in cart_items_to_delete]).delete()
    order = Order.objects.create(owner=owner)

    for order_item in order_items:
        order_item.order = order
    OrderItem.objects.bulk_create(order_items)

    return order


@transaction.atomic()
def apply_coupon(order: Order, coupon: Coupon) -> Order | None:
    now = datetime.now(tz=timezone('Asia/Tehran'))
    if coupon.expiration_date < now:
        return None

    order.discount_percent += coupon.discount_percent
    order.coupon = coupon
    order.full_clean()
    order.save()
    coupon.max_usage_limit -= 1
    coupon.full_clean()
    coupon.save()

    return order


@transaction.atomic()
def discard_coupon(order: Order, coupon: Coupon) -> Order | None:
    order.discount_percent -= coupon.discount_percent
    order.coupon = None
    order.full_clean()
    order.save()
    coupon.max_usage_limit += 1
    coupon.full_clean()
    coupon.save()

    return order


@transaction.atomic()
def cancel_order(order: Order) -> Order:
    order.status = ORDER_STATUS_CANCELLED
    for item in order.items.all():
        item.product.quantity += item.quantity
        item.product.save()
    if order.coupon is not None:
        discard_coupon(order=order, coupon=order.coupon)
    order.save()
    return order


def set_order_status(order: Order, status: str) -> Order:
    order.status = status
    order.save()
    return order
