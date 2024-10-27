from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import FileExtensionValidator
from django.db import models

from . import choices
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=choices.USER_ROLE_CHOICES,
        verbose_name='نقش'
    )

    is_active = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def is_staff(self):
        return self.role == choices.USER_ROLE_ADMIN

    class Meta:
        ordering = ('email',)


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
