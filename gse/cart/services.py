from .models import Cart, CartItem
from .selectors import get_cart_item_by_product_id


def add_cart_item(cart: Cart, item_data: dict) -> CartItem:
    product = item_data.get('product')
    quantity = item_data.get('quantity')

    item_obj = get_cart_item_by_product_id(product_id=product.id, owner_id=cart.owner.id)
    if item_obj and (product.id == item_obj.product.id):
        item_obj.quantity += quantity
        item_obj.save()
        return item_obj

    return CartItem.objects.create(cart=cart, **item_data)
