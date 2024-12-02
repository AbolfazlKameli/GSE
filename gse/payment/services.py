import json
import os
from decimal import Decimal

import requests
from django.conf import settings
from django.db import transaction

from gse.orders.choices import ORDER_STATUS_SUCCESS
from gse.orders.models import Order
from gse.orders.services import set_order_status
from .choices import PAYMENT_STATUS_SUCCESS, PAYMENT_STATUS_FAILED
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


def verify(status, authority, amount, order):
    if status == 'OK':
        req_header = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        req_data = {
            "merchant_id": settings.MERCHANT,
            "amount": amount,
            "authority": authority
        }
        req = requests.post(url=settings.ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
        ref_id = str(req.json()['data'].get('ref_id'))
        if ref_id == 'None':
            return {
                'Error': 'اطلاعات ارسالی با اطلاعات موجود مطابقت ندارند.',
                'code': req.status_code
            }

        payment = create_payment(
            order=order,
            authority_id=authority,
            ref_id=ref_id,
            amount=amount,
            response_json=req.json(),
            response_code=req.json()['data']['code']
        )

        if len(req.json()['errors']) == 0:
            t_status = req.json()['data']['code']
            if t_status == 100:
                set_payment_status(payment, PAYMENT_STATUS_SUCCESS)
                set_order_status(order, ORDER_STATUS_SUCCESS)
                return {
                    'message': 'پرداخت موفق بود.',
                    'ref_id': str(req.json()['data']['ref_id']),
                    'code': 200
                }
            elif t_status == 101:
                set_payment_status(payment, PAYMENT_STATUS_FAILED)
                return {
                    'message': 'تراکنش ارسال شد.',
                    'details': str(req.json()['data']['message']),
                    'code': req.status_code
                }
            else:
                set_payment_status(payment, PAYMENT_STATUS_FAILED)
                return {
                    'Error': str(req.json()['data']['message']),
                    'code': req.status_code
                }
        else:
            set_payment_status(payment, PAYMENT_STATUS_FAILED)
            e_code = req.json()['errors']['code']
            e_message = req.json()['errors']['message']
            return {
                'Error': e_message,
                'code': e_code
            }
    else:
        return {
            'Error': 'تراکنش ناموفق بود یا توسط کاربر لفو شد.',
            'code': 400
        }
