from pathlib import Path

import boto3
from django.apps import apps
from django.conf import settings
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.utils.text import slugify

from gse.utils import Singleton
from .validators import validate_file_type


def slugify_title(title: str) -> str:
    return slugify(title, allow_unicode=True)


class Bucket(metaclass=Singleton):
    def __init__(self):
        session = boto3.session.Session()
        self.connection = session.client(
            service_name=settings.AWS_SERVICE_NAME,
            aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    def delete_file_object(self, key):
        self.connection.delete_object(Bucket=self.bucket_name, Key=key)
        return True


def upload_media(product, path, file_name):
    product_media = apps.get_model('products', 'ProductMedia')
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
        instance = product_media(product=product, media=media, media_type=media_type)
        instance.save()

    storage.delete(file_name)
    return True
