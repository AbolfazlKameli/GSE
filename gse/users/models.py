from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from . import choices
from .managers import UserManager
from .validators import validate_iranian_phone_number


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=50)
    role = models.CharField(
        max_length=20,
        choices=choices.USER_ROLE_CHOICES,
        verbose_name='نقش'
    )

    is_active = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='created date')
    updated_date = models.DateTimeField(auto_now=True, verbose_name='updated date')

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return f'{self.email}'

    @property
    def is_staff(self):
        return self.role == choices.USER_ROLE_ADMIN

    @property
    def is_support(self):
        return self.role == choices.USER_ROLE_SUPPORT

    @property
    def is_customer(self):
        return self.role == choices.USER_ROLE_CUSTOMER

    class Meta:
        ordering = ('created_date',)
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'


class UserProfile(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=50, default='', verbose_name='first name')
    last_name = models.CharField(max_length=50, default='', verbose_name='last name')
    phone_number = models.CharField(
        max_length=12,
        validators=[validate_iranian_phone_number],
        unique=True,
        null=True,
        blank=True,
        verbose_name='phone number'
    )
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='created date')
    updated_date = models.DateTimeField(auto_now=True, verbose_name='updated date')

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f'{self.owner}'


class Address(models.Model):
    owner_profile = models.OneToOneField(User, on_delete=models.CASCADE, related_name='address', verbose_name='owner')
    address = models.TextField()
    postal_code = models.CharField(max_length=10, unique=True)
