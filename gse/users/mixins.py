from django.core.exceptions import ValidationError
from rest_framework import exceptions as rest_exceptions
from rest_framework.response import Response
from rest_framework import status

from .models import User
from .services import get_error_message


class ApiErrorsMixin:
    """
    Mixin that transforms Django and Python exceptions into rest_framework ones.
    Without the mixin, they return 500 status code which is not desired.
    """
    expected_exceptions = {
        ValueError: rest_exceptions.ValidationError,
        ValidationError: rest_exceptions.ValidationError,
        PermissionError: rest_exceptions.PermissionDenied,
        User.DoesNotExist: rest_exceptions.NotAuthenticated
    }

    def handle_exception(self, exc):
        if isinstance(exc, tuple(self.expected_exceptions.keys())):
            drf_exception_class = self.expected_exceptions[exc.__class__]
            error_message = get_error_message(exc)
            status_code = self.get_status_code(drf_exception_class)
            return Response(
                {"detail": error_message},
                status=status_code
            )
        return super().handle_exception(exc)

    def get_status_code(self, drf_exception_class):
        if drf_exception_class == rest_exceptions.ValidationError:
            return status.HTTP_400_BAD_REQUEST
        elif drf_exception_class == rest_exceptions.PermissionDenied:
            return status.HTTP_403_FORBIDDEN
        elif drf_exception_class == rest_exceptions.NotAuthenticated:
            return status.HTTP_401_UNAUTHORIZED
        return status.HTTP_500_INTERNAL_SERVER_ERROR
