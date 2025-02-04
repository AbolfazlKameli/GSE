from celery import shared_task

from .services import Bucket, upload_media

bucket = Bucket()


@shared_task
def upload(product, path, file_name):
    return upload_media(product, path, file_name)


@shared_task
def delete_product_picture(file):
    bucket.delete_file_object(key=file)
