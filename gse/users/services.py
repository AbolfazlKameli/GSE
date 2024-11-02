from random import randint

from django.db import transaction
from django.core.cache import cache

from .models import User


def create_user(*, email: str, password) -> User:
    return User.objects.create_user(email=email, password=password)


@transaction.atomic
def register(*, email: str, password: str) -> User:
    user = create_user(email=email, password=password)
    return user


def generate_otp_code(*, phone_number: str):
    while True:
        otp_code: str = str(randint(10000, 99999))

        if not cache.get(f'otp_code_{otp_code}'):
            cache.set(f'otp_code_{phone_number}', otp_code, timeout=300)
            cache.set(f'otp_code_{otp_code}', phone_number, timeout=300)
            return otp_code


def check_otp_code(*, phone_number: str, otp_code: str):
    stored_code: str = cache.get(f'otp_code_{phone_number}')
    return stored_code == otp_code
