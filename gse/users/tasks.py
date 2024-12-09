from celery import shared_task

from gse.utils import senders
from .services import generate_otp_code


@shared_task
def send_verification_email(email_address: str, content: str, subject: str):
    otp_code = generate_otp_code(email=email_address)
    content = f'{content}\n{otp_code}'
    # if action == 'reset_password':
    #     code = f"http://{settings.DOMAIN}{reverse('users:set-password', args=[otp_code])}"
    send_email.send_link(email=email_address, content=content, subject=subject)
