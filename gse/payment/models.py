from django.db import models

from gse.orders.models import Order
from .choices import PAYMENT_STATUS_CHOICES, PAYMENT_STATUS_PENDING


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payment', db_index=True)
    authority_id = models.CharField(max_length=250)
    ref_id = models.CharField(max_length=250, blank=True, null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=0)
    response_json = models.JSONField(blank=True, null=True)
    response_code = models.IntegerField(blank=True, null=True)
    status = models.CharField(
        choices=PAYMENT_STATUS_CHOICES,
        verbose_name='وضعیت پرداخت',
        default=PAYMENT_STATUS_PENDING,
        max_length=10
    )
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.order.id} - {self.ref_id} - {self.status}'
