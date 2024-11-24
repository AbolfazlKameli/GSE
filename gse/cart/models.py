from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from gse.products.models import Product
from gse.users.models import User


class Cart(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def get_total_price(self):
        return round(sum(
            item.product.final_price * item.quantity for item in self.items.select_related('product').all()
        ))

    def get_total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    class Meta:
        ordering = ('-created_date',)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def get_total_price(self):
        return round(self.quantity * self.product.final_price)

    def clean(self, *args, **kwargs):
        if self.product.quantity < self.quantity:
            raise ValidationError('این تعداد از این محصول در انبار موجود نمیباشد.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('-created_date',)
