from django.contrib.auth.models import BaseUserManager

from .choices import USER_ROLE_ADMIN


class UserManager(BaseUserManager):
    def create_user(self, email, role, password):
        if not email:
            raise ValueError('کاربران باید ایمیل داشته باشند.')

        user = self.model(role=role, email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email=email,
            role=USER_ROLE_ADMIN,
            password=password
        )
        user.is_active = True
        user.save(using=self._db)
        return user
