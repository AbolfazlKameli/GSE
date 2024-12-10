from decouple import config
from django.conf import settings
from django.core.mail import send_mail
from kavenegar import *


def send_link(*, email: str, content: str, subject: str):
    send_mail(
        subject=subject,
        message=content,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
    )


def send_sms(*, phone_number: str, content: str):
    api = KavenegarAPI(config('KAVENEGAR_API_KEY'))
    sender = config('KAVENEGAR_PHONE_NUMBER', default='2000500666')
    params = {'sender': sender, 'receptor': phone_number, 'message': content}
    try:
        response = api.sms_send(params)
    except APIException:
        return False
    except HTTPException:
        return False
    return response
