from typing import Literal

from celery import shared_task

from .services import generate_otp_code, send_link, send_sms


@shared_task
def send_verification_email(
        email_address: str,
        content: str,
        subject: str,
        action: Literal['verify', 'reset_password']
):
    otp_code = generate_otp_code(email=email_address, action=action)
    content = f'{content}\n{otp_code}'
    send_link(email=email_address, content=content, subject=subject)


@shared_task
def send_verification_sms(phone_number: str, action: Literal['verify', 'reset_password']):
    otp_code = generate_otp_code(phone_number=phone_number, action=action)
    content = f'کد تایید شما:\n {otp_code}'
    result = send_sms(phone_number=phone_number, content=content)
    return result
