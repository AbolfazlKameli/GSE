from typing import Type

from django.db import models


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
