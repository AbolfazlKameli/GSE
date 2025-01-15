from celery import shared_task

from .models import Product
from .serializers import ProductMediaSerializer


@shared_task
def upload_product_media(*, product: Product, serializer: ProductMediaSerializer):
    serializer.save(product=product)
    return serializer.data
