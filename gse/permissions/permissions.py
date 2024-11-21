from rest_framework.permissions import BasePermission, SAFE_METHODS

from gse.users.choices import USER_ROLE_ADMIN, USER_ROLE_SUPPORT


class NotAuthenticated(BasePermission):
    message = 'شما قبلاً احراز هویت کرده‌اید!'

    def has_permission(self, request, view):
        return bool(request.user and not request.user.is_authenticated)


class IsAdminOrOwner(BasePermission):
    message = 'شما مالک نیستید!'

    def has_object_permission(self, request, view, obj):
        condition = obj.id
        if hasattr(obj, 'owner'):
            condition = obj.owner.id
        return bool(
            request.user and request.user.is_authenticated and (
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
