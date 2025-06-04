from datetime import datetime
from random import randint, SystemRandom
from typing import Dict, Any
from urllib.parse import urlencode

from decouple import config
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from kavenegar import *
from oauthlib.common import UNICODE_ASCII_CHARACTER_SET
from pytz import timezone
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token

from .models import User, UserProfile
from .selectors import get_user_by_email

GOOGLE_ID_TOKEN_INFO_URL = 'https://www.googleapis.com/oauth2/v3/tokeninfo'
GOOGLE_ACCESS_TOKEN_OBTAIN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'
GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'


def create_user(*, email: str, password) -> User:
    return User.objects.create_user(email=email, password=password)


def update_last_login(email) -> User | None:
    user: User | None = get_user_by_email(email=email)
    if user is None:
        return user
    user.last_login = datetime.now(tz=timezone('Asia/Tehran'))
    user.save(update_fields=['last_login'])
    return user


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


@transaction.atomic
def register(*, email: str, password: str = None, is_active: bool = False) -> User:
    user = create_user(email=email, password=password)
    if is_active:
        user.is_active = True
        user.save()
    return user


@transaction.atomic
def update_profile(
        *,
        user: User,
        user_data: dict = None,
        profile_data: dict = None,
        address_data: dict = None
) -> UserProfile:
    profile = user.profile
    address = user.address

    if user_data is not None:
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

    if profile_data is not None:
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

    if address_data is not None:
        for attr, value in address_data.items():
            setattr(address, attr, value)
        address.save()

    return profile


def generate_otp_code(*, email: str = None, phone_number: str = None) -> str:
    while True:
        otp_code: str = str(randint(10000, 99999))
        if not cache.get(f'otp_code_{otp_code}'):
            if phone_number:
                cache.set(f'otp_code_{phone_number}', otp_code, timeout=300)
                cache.set(f'otp_code_{otp_code}', phone_number, timeout=300)
            elif email:
                cache.set(f'otp_code_{email}', otp_code, timeout=300)
                cache.set(f'otp_code_{otp_code}', email, timeout=300)
            return otp_code


def check_otp_code(*, otp_code: str, phone_number: str = None, email: str = None) -> bool:
    stored_code = ''
    if phone_number:
        stored_code: str = cache.get(f'otp_code_{phone_number}')
    elif email:
        stored_code: str = cache.get(f'otp_code_{email}')

    if stored_code == otp_code:
        cache.delete(f'otp_code_{email}')
        cache.delete(f'otp_code_{phone_number}')
        cache.delete(f'otp_code_{otp_code}')
        return stored_code == otp_code
    else:
        return False


def generate_tokens_for_user(user: User) -> tuple[Any, Token]:
    """
    Generate access and refresh tokens for the given user
    """
    serializer = TokenObtainPairSerializer()
    token_data = serializer.get_token(user)
    access_token = token_data.access_token
    refresh_token = token_data

    user: User | None = update_last_login(user.email)
    if user is None:
        pass

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
    if not response.ok:
        raise ValidationError('Failed to obtain access token from Google.')
    access_token = response.json()['access_token']
    return access_token


def google_get_user_info(*, access_token: str) -> Dict[str, Any]:
    response = requests.get(
        GOOGLE_USER_INFO_URL,
        params={'access_token': access_token}
    )

    if not response.ok:
        raise ValidationError('Failed to obtain user info from Google.')
    return response.json()


def get_error_message(err):
    if hasattr(err, 'message'):
        return str(err.message)
    elif hasattr(err, 'messages'):
        return ', '.join(err.messages)
    return str(err)


def generate_state_session_token(length: int = 30, chars: str = UNICODE_ASCII_CHARACTER_SET) -> str:
    rand = SystemRandom()
    state = "".join(rand.choice(chars) for _ in range(length))
    return state


def get_authorization_url() -> tuple[str, str]:
    state = generate_state_session_token()
    redirect_uri = f'https://{settings.DOMAIN}/users/register/google/auth/callback/'
    scopes = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid",
    ]

    params = {
        "response_type": "code",
        "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "scope": " ".join(scopes),
        "state": state,
        "access_type": "offline",
        "include_granted_scopes": "true",
        "prompt": "select_account",
    }

    query_params = urlencode(params)
    authorization_url = f"{GOOGLE_AUTH_URL}?{query_params}"

    return authorization_url, state
