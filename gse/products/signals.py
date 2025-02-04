from django.db.models.signals import pre_delete
from django.dispatch import receiver

from gse.products.models import ProductMedia
from .tasks import delete_product_picture


@receiver(pre_delete, sender=ProductMedia)
def delete_media_files(sender, instance, **kwargs):
    if instance.media:
        delete_product_picture.delay(instance.media.name)
