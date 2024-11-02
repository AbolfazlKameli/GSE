from .models import User


def get_user_by_email(email: str) -> User | None:
    try:
        return User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return None
