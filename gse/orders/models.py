from django.core.validators import MaxValueValidator
from django.db import models

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
