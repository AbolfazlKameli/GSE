from datetime import datetime

from django.db import transaction
from pytz import timezone

from gse.cart.models import Cart, CartItem
from gse.products.models import Product
from gse.products.selectors import get_products_for_update_by_ids
from gse.users.models import User
from .choices import ORDER_STATUS_CANCELLED
from .models import Order, Coupon, OrderItem


@transaction.atomic()
def create_order(owner: User, items: list[dict[str, int | Product]]) -> Order:
    cart = Cart.objects.select_related('owner').prefetch_related('items__product').get(owner=owner)

    products_ids = [item['product'].id for item in items]
    products = get_products_for_update_by_ids(products_ids)

    products_to_update = []
    cart_items_to_delete = []
    order_items = []

    for item in items:
        product_id = item.get('product').id
        product = products[product_id]
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
    items = order.items.select_related('product')
    product_ids = [item.product_id for item in items]
    products = get_products_for_update_by_ids(product_ids)
    for item in items:
        product = products[item.product_id]
        product.quantity += item.quantity
    Product.objects.bulk_update(products.values(), ['quantity'])
    order.save()
    return order


def set_order_status(order: Order, status: str) -> Order:
    order.status = status
    order.save()
    return order
