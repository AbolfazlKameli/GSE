import boto3
from django.conf import settings
from django.db import transaction

from gse.utils import Singleton
from .models import Product, ProductCategory, ProductDetail


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


@transaction.atomic
def create_product(
        title: str,
        quantity: int,
        description: str,
        unit_price: int,
        details: dict,
        categories: list[ProductCategory],
        available: bool = False,
        discount_percent: int = 0,
):
    product: Product = Product.objects.create(
        title=title,
        quantity=quantity,
        description=description,
        unit_price=unit_price,
        discount_percent=discount_percent,
        available=available,
    )

    for category in categories:
        product.category.add(category)

    product_details = [ProductDetail(**detail, product=product) for detail in details]
    ProductDetail.objects.bulk_create(product_details)
