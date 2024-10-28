from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import FileExtensionValidator
from django.db import models

from . import choices
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
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
    avatar = models.ImageField(
        upload_to='avatars',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])]
    )
    bio = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f'{self.owner}'
