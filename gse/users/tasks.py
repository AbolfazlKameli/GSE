from celery import shared_task

from .services import generate_otp_code, send_link, send_sms


@shared_task(bind=True)
def send_verification_email(self, email_address: str, content: str, subject: str):
    otp_code = generate_otp_code(email=email_address)
    content = f'{content}\n{otp_code}'

    try:
        result = send_link(email=email_address, content=content, subject=subject)
        return result
    except Exception as e:
        self.retry(exc=e, max_retries=3, countdown=5)


@shared_task(bind=True)
def send_verification_sms(self, phone_number: str):
    otp_code = generate_otp_code(phone_number=phone_number)
    content = f'کد تایید شما:\n {otp_code}'

    try:
        result = send_sms(phone_number=phone_number, content=content)
        return result
    except Exception as e:
        self.retry(exc=e, max_retries=3, countdown=5)
