from typing import Type

from django.db import models
from rest_framework import status
from rest_framework.response import Response


class Singleton(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


def is_child_of(
        parent_type: Type[models.Model],
        child_type: Type[models.Model],
        parent_id: int,
        child_id: int,
        parent_related_field_name=None
) -> bool:
    parent_name = parent_type.__name__.lower()

    if parent_related_field_name is None:
        parent_related_field_name = f'{parent_name}_id'

    return child_type.objects.filter(
        id=child_id,
        **{parent_related_field_name: parent_id}
    ).exists()


def format_errors(errors):
    formatted_errors = {}
    for field, error in errors.items():
        if isinstance(error, list):
            if all(isinstance(item, dict) for item in error):
                formatted_errors[field] = [format_errors(item) for item in error]
            else:
                formatted_errors[field] = error[0]
        elif isinstance(error, dict):
            formatted_errors[field] = {key: val[0] if isinstance(val, list) else val for key, val in error.items()}
        else:
            formatted_errors[field] = error
    return formatted_errors


def update_response(response, message: str):
    """Handles the response for update operations."""
    if response.status_code == 200:
        return Response(data={'data': {'message': message}}, status=status.HTTP_200_OK)
    return response
