from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from gse.products.models import Product
from gse.users.models import User


class Cart(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def get_total_price(self):
        return sum(
            item.product.get_price() * item.quantity for item in self.items.all()
        )


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
