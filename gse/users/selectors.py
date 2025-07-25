from django.core.cache import cache

from .choices import USER_ROLE_ADMIN, USER_ROLE_SUPPORT
from .models import User


def get_user_by_email(email: str) -> User | None:
    return User.objects.prefetch_related('profile', 'address').filter(email__iexact=email).first()

def is_email_taken(email: str) -> bool:
    return User.objects.filter(email__exact=email).exists()

def get_user_by_phone_number(phone_number: str) -> User | None:
    return User.objects.select_related('profile').filter(profile__phone_number__exact=phone_number).first()


def get_admins_and_supporters_ids() -> list[int]:
    cached_data = cache.get("admins_and_supporters_ids")
    if cached_data is not None:
        return cached_data
    result = [user.id for user in User.objects.filter(role__in=[USER_ROLE_ADMIN, USER_ROLE_SUPPORT])]
    cache.set("admins_and_supporters_ids", result, timeout=3600)
    return result
