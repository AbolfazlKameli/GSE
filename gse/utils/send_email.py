from django.conf import settings
from django.core.mail import send_mail


def send_link(*, email: str, content: str, subject: str):
    send_mail(
        subject=subject,
        message=content,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
    )
