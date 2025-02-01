import boto3
from django.conf import settings
from django.utils.text import slugify

from gse.utils.utils import Singleton


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
