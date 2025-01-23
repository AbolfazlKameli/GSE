from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models

from gse.products.models import Product
from gse.users.models import User
from .choices import ORDER_STATUS_CHOICES, ORDER_STATUS_PENDING


class Order(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', db_index=True)
    status = models.CharField(
        choices=ORDER_STATUS_CHOICES,
        verbose_name='وضعیت سفارش',
        default=ORDER_STATUS_PENDING,
        max_length=10,
        db_index=True
    )
    discount_percent = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)], default=0, db_index=True)
    coupon = models.ForeignKey(
        'Coupon',
        on_delete=models.SET_NULL,
        related_name='order',
        blank=True,
        null=True,
        db_index=True
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def remove_if_no_item(self):
        items_count = self.items.count()
        if items_count == 0:
            self.delete()

    @property
    def total_price(self):
        if self.discount_percent > 0:
            price = round(sum(item.total_price for item in self.items.all()))
            discount_amount = price * Decimal(self.discount_percent / 100)
            discounted_amount = price - discount_amount
            return round(discounted_amount)
        else:
            return round(sum(item.total_price for item in self.items.all()))

    class Meta:
        ordering = ('-updated_date',)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items', db_index=True)
    quantity = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)], db_index=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return self.quantity * self.product.get_price()

    def clean(self):
        if self.quantity > self.product.quantity:
            raise ValidationError('این تعداد از این محصول در انبار موجود نمیباشد.')

    def save(self, *args, **kwargs):
        self.clean()
        if self.quantity == 0:
            self.delete()
        else:
            super().save(*args, **kwargs)

    class Meta:
        ordering = ('-created_date',)


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, db_index=True)
    discount_percent = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)], default=0, db_index=True)
    max_usage_limit = models.PositiveIntegerField(default=100, db_index=True)
    expiration_date = models.DateTimeField(db_index=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_date',)
