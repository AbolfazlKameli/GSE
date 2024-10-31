from django.db import transaction

from .models import User


def create_user(*, email: str, password) -> User:
    return User.objects.create_user(email=email, password=password)


@transaction.atomic
def register(*, email: str, password: str) -> User:
    user = create_user(email=email, password=password)
    return user
