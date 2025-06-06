from .models import Cart, CartItem


def get_all_carts() -> list[Cart]:
    return Cart.objects.select_related('owner').prefetch_related('items').all()


def get_all_cart_items() -> list[CartItem]:
    return CartItem.objects.select_related('cart', 'product').all()


def get_cart_item_by_product_id(product_id: int, owner_id: int) -> CartItem | None:
    return CartItem.objects.select_related('cart__owner', 'product') \
        .filter(product_id=product_id, cart__owner_id=owner_id) \
        .first()


def get_cart_item_by_id(item_id: int) -> CartItem | None:
    return CartItem.objects.filter(id=item_id).first()


def get_cart_by_item_id(item_id: int) -> Cart | None:
    return Cart.objects.filter(items__id=item_id).first()
