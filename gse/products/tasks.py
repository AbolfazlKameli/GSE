from celery import shared_task

from .services import Bucket

bucket = Bucket()


@shared_task
def delete_product_picture(file):
    bucket.delete_file_object(key=file)
