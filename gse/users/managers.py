from django.apps import apps
from django.contrib.auth.models import BaseUserManager
from django.db import transaction

from .choices import USER_ROLE_ADMIN, USER_ROLE_CUSTOMER


class UserManager(BaseUserManager):
    @transaction.atomic
    def create_user(self, email, password, role=USER_ROLE_CUSTOMER):
        if not email:
            raise ValueError('کاربران باید ایمیل داشته باشند.')

        user = self.model(role=role, email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)

        # using get_model to avoid the circular import issue with UserProfile model
        profile = apps.get_model('users', 'UserProfile')
        profile.objects.create(owner=user)

        cart = apps.get_model('cart', 'Cart')
        cart.objects.create(owner=user)

        address = apps.get_model('users', 'Address')
        address.objects.create(owner_profile=user)

        return user

    @transaction.atomic
    def create_superuser(self, email, password):
        user = self.create_user(
            email=email,
            role=USER_ROLE_ADMIN,
            password=password
        )
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
