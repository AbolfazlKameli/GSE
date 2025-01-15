from pathlib import Path

from celery import shared_task
from django.core.files import File
from django.core.files.storage import FileSystemStorage

from .models import ProductMedia
from .validators import validate_file_type


@shared_task
def upload(product, path, file_name):
    allowed_types = {
        'images': ['image/jpeg', 'image/png', 'image/jpg'],
        'videos': ['video/mp4']
    }
    storage = FileSystemStorage()
    path_object = Path(path)
    with path_object.open(mode='rb') as file:
        media = File(file, name=path_object.name)
        media_type = validate_file_type(file=media, expected_types=allowed_types)
        if media_type is None:
            return False
        instance = ProductMedia(product=product, media_url=media, media_type=media_type)
        instance.save()

    storage.delete(file_name)
    return True
