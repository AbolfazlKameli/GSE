from random import randint
from typing import Dict, Any

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, UserProfile

GOOGLE_ID_TOKEN_INFO_URL = 'https://www.googleapis.com/oauth2/v3/tokeninfo'
GOOGLE_ACCESS_TOKEN_OBTAIN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'


def create_user(*, email: str, password) -> User:
    return User.objects.create_user(email=email, password=password)


@transaction.atomic
def register(*, email: str, password: str = None, is_active: bool = False) -> User:
    user = create_user(email=email, password=password)
    if is_active:
        user.is_active = True
        user.save()
    return user


@transaction.atomic
def update_profile(*, user_id: int, profile_data: dict = None) -> UserProfile:
    profile = UserProfile.objects.get(owner_id__exact=user_id)
    if profile_data:
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()
    return profile


def generate_otp_code(*, email: str) -> str:
    while True:
        otp_code: str = str(randint(10000, 99999))

        if not cache.get(f'otp_code_{otp_code}'):
            cache.set(f'otp_code_{email}', otp_code, timeout=300)
            cache.set(f'otp_code_{otp_code}', email, timeout=300)
            return otp_code


def check_otp_code(*, email: str, otp_code: str) -> bool:
    stored_code: str = cache.get(f'otp_code_{email}')
    return stored_code == otp_code


def generate_tokens_for_user(user):
    """
    Generate access and refresh tokens for the given user
    """
    serializer = TokenObtainPairSerializer()
    token_data = serializer.get_token(user)
    access_token = token_data.access_token
    refresh_token = token_data
    return access_token, refresh_token


def google_get_access_token(*, code: str, redirect_uri: str) -> str:
    data = {
        'code': code,
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }

    response = requests.post(GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)
    print(response.text)

    if not response.ok:
        raise ValidationError('Failed to obtain access token from Google.')
    print('=' * 90)
    access_token = response.json()['access_token']

    return access_token


def google_get_user_info(*, access_token: str) -> Dict[str, Any]:
    response = requests.get(
        GOOGLE_USER_INFO_URL,
        params={'access_token': access_token}
    )

    if not response.ok:
        raise ValidationError('Failed to obtain user info from Google.')

    print(response.text)

    return response.json()


def get_error_message(err):
    if hasattr(err, 'message'):
        return str(err.message)
    elif hasattr(err, 'messages'):
        return ', '.join(err.messages)
    return str(err)
