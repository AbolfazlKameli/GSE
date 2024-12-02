import json
import os
from decimal import Decimal

import requests
from django.conf import settings
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


def payment_request(amount: int, phone: str, email: str):
    req_data = {
        "merchant_id": settings.MERCHANT,
        "amount": amount,
        "callback_url": settings.CALLBACK_URL,
        "description": 'description',
        "metadata": {"mobile": phone, "email": email}
    }
    req_header = {"accept": "application/json",
                  "content-type": "application/json'"}
    try:
        req = requests.post(url=settings.ZP_API_REQUEST, data=json.dumps(req_data), headers=req_header)
        authority = req.json()['data']['authority']
        if len(req.json()['errors']) == 0:
            return {
                'authority': authority,
                'url': settings.ZP_API_STARTPAY + authority,
                'code': 200
            }
        else:
            e_code = req.json()['errors']['code']
            e_message = req.json()['errors']['message']
            return {
                'ErrorName': 'Unknown',
                'Error': e_message,
                'code': e_code
            }
    except requests.exceptions.ConnectionError:
        return {
            'ErrorName': 'ConnectionError',
            'Error': 'اتصال ناموفق',
            'code': 400
        }
    except requests.exceptions.Timeout:
        return {
            'ErrorName': 'TimeOut',
            'Error': 'عملیات ناموفق',
            'code': 400
        }
