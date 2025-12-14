from gse.products.models import Product

from .models import Cart, CartItem
from .selectors import get_cart_item_by_product_id


def add_cart_item(cart: Cart, product: Product) -> CartItem:
    item_obj = get_cart_item_by_product_id(product_id=product.id, owner_id=cart.owner.id)
    if item_obj and (product.id == item_obj.product.id):
        item_obj.quantity += 1
        item_obj.save()
        return item_obj

    return CartItem.objects.create(cart=cart, product=product)
