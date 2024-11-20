from .models import Cart


def check_cart_total_quantity(cart: Cart) -> bool:
    total_quantity = cart.get_total_quantity()
    print(total_quantity > 100)
    if total_quantity > 99:
        return False
    return True
