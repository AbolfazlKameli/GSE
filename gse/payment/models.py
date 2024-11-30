from django.db import models

from gse.orders.models import Order
from .choices import PAYMENT_STATUS_CHOICES, PAYMENT_STATUS_PENDING


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    authority_id = models.CharField(max_length=250)
    ref_id = models.CharField(max_length=250)
    amount = models.DecimalField(max_digits=15, decimal_places=0)
    response_json = models.JSONField()
    response_code = models.IntegerField()
    status = models.CharField(
        choices=PAYMENT_STATUS_CHOICES,
        verbose_name='وضعیت پرداخت',
        default=PAYMENT_STATUS_PENDING,
        max_length=10
    )
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.order.id} - {self.ref_id} - {self.status}'
