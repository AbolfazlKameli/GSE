from .models import Cart


def get_all_carts() -> list[Cart]:
    return Cart.objects.select_related('owner').all()
