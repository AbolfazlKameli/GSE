from django.contrib.auth.models import BaseUserManager

from .choices import USER_ROLE_ADMIN


class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, role, password):
        if not first_name:
            raise ValueError('کاربران باید نام داشته باشند.')
        if not last_name:
            raise ValueError('کاربران باید نام خانوادگی داشته باشند.')
        if not email:
            raise ValueError('کاربران باید ایمیل داشته باشند.')

        user = self.model(first_name=first_name, last_name=last_name, role=role, email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, password):
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            role=USER_ROLE_ADMIN,
            password=password
        )
        user.is_active = True
        user.save(using=self._db)
        return user
