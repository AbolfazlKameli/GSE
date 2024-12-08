from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAdminUser

from gse.users.choices import USER_ROLE_ADMIN, USER_ROLE_SUPPORT


class NotAuthenticated(BasePermission):
    message = 'شما قبلاً احراز هویت کرده‌اید!'

    def has_permission(self, request, view):
        return bool(request.user and not request.user.is_authenticated)


class IsAdminOrSupporter(BasePermission):
    message = 'شما دسترسی لازم برای انجام این عملیات را ندارید.'

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and (request.user.role in (USER_ROLE_ADMIN, USER_ROLE_SUPPORT)))


class IsAdminOrOwner(BasePermission):
    message = 'شما مالک نیستید!'

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        condition = obj.id
        if hasattr(obj, 'owner'):
            condition = obj.owner.id
        return bool(
            request.user and (
                    condition == request.user.id or request.user.role in (USER_ROLE_ADMIN, USER_ROLE_SUPPORT)
            )
        )


class IsSupporterOrAdminOrReadOnly(BasePermission):
    message = 'برای دسترسی به این صفحه باید ادمین یا پشتیبان باشید.'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user and request.user.is_authenticated and request.user.role in (USER_ROLE_ADMIN, USER_ROLE_SUPPORT)
        )


class FullCredentialsUser(BasePermission):
    message = 'اطلاعات کاربری خود مثل شماره تلفن، آدرس و... را کامل کنید.'

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        credentials = [
            request.user.profile.phone_number,
            request.user.address,
            request.user.profile.first_name,
            request.user.profile.last_name,
        ]
        return all(credentials)
