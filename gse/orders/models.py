from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
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


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    total_price = models.DecimalField(
        validators=[MinValueValidator(Decimal(0))],
        max_digits=15,
        decimal_places=0,
        default=0
    )
    quantity = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)])
    created_date = models.DateTimeField(auto_now_add=True)
    updated_data = models.DateTimeField(auto_now=True)


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)], default=0)
    max_usage_limit = models.PositiveIntegerField(default=100)
    expiration_date = models.DateTimeField()
    is_usable = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
