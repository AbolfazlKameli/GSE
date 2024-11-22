from django.core.validators import MaxValueValidator
from django.db import models

from gse.products.models import Product
from gse.users.models import User
from .choices import ORDER_STATUS_CHOICES, ORDER_STATUS_PENDING


class Order(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(
        choices=ORDER_STATUS_CHOICES,
        verbose_name='وضعیت سفارش',
        default=ORDER_STATUS_PENDING,
        max_length=10
    )
    discount_percent = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)], default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return round(sum(
            item.quantity * item.product.final_price for item in self.items.select_related('product').all()
        ))


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)])
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return self.quantity * self.product.final_price

    def save(self, *args, **kwargs):
        if self.quantity == 0:
            self.delete()
        else:
            super().save(*args, **kwargs)


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)], default=0)
    max_usage_limit = models.PositiveIntegerField(default=100)
    expiration_date = models.DateTimeField()
    is_usable = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
