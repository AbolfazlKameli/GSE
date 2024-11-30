import io

import boto3
from django.conf import settings


class SingletonBucket(type):
    _instance = None

    def __call__(self, *args, **kwargs):
        if self._instance is None:
            self._instance = super().__call__(*args, **kwargs)
        return self._instance


class Bucket(metaclass=SingletonBucket):
    def __init__(self):
        session = boto3.session.Session()
        self.connection = session.client(
            service_name=settings.AWS_SERVICE_NAME,
            aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    def delete_object(self, key):
        self.connection.delete_object(Bucket=self.bucket_name, Key=key)
        return True

    def upload_file(self, file_path: str, file_content: bytes, content_type: str = None) -> str:
        try:
            self.connection.upload_fileobj(
                io.BytesIO(file_content),
                self.bucket_name,
                file_path,
                ExtraArgs={"ContentType": content_type}
            )
            return file_path
        except Exception as e:
            raise Exception(f"Failed to upload file to S3: {e}") from e
