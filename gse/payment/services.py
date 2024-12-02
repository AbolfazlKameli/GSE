import os
from decimal import Decimal

from django.db import transaction

from gse.orders.models import Order
from .models import Payment

os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'core.settings.settings')


@transaction.atomic()
def create_payment(
        *,
        order: Order,
        authority_id: str,
        amount: Decimal,
        ref_id: str = None,
        response_json=None,
        response_code: int = None
) -> Payment:
    payment: Payment = Payment.objects.create(
        order=order,
        authority_id=authority_id,
        ref_id=ref_id,
        amount=amount,
        response_json=response_json,
        response_code=response_code
    )
    return payment


@transaction.atomic()
def set_payment_status(payment: Payment, status: str) -> Payment:
    payment.status = status
    payment.save()
    return payment
