from django.db import transaction

from .models import User, UserProfile


def create_user(*, username: str, email: str, password) -> User:
    return User.objects.create_user(username, email, password)


@transaction.atomic
def register(*, username: str, email: str, password: str) -> User:
    user = create_user(username=username, email=email, password=password)
    return user
