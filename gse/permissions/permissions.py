from rest_framework.permissions import BasePermission, SAFE_METHODS

from gse.users.choices import USER_ROLE_ADMIN, USER_ROLE_SUPPORT


class NotAuthenticated(BasePermission):
    message = 'You already authenticated!'

    def has_permission(self, request, view):
        return bool(request.user and not request.user.is_authenticated)


class IsAdminOrOwnerOrReadOnly(BasePermission):
    message = 'you are not the owner!'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        condition = obj.id
        if hasattr(obj, 'owner'):
            condition = obj.owner.id
        return bool(
            request.user and request.user.is_authenticated and (
                    condition == request.user.id or request.user.role in (USER_ROLE_ADMIN, USER_ROLE_SUPPORT)
            )
        )


class IsAdminOrOwner(BasePermission):
    message = 'you are not owner or admin'

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
    message = 'دسترسی ندارید'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user and request.user.is_authenticated and request.user.role in (USER_ROLE_ADMIN, USER_ROLE_SUPPORT)
        )
