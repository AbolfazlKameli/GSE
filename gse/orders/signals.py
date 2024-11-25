from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Order


@receiver(post_save, sender=Order)
def check_order_item_count(sender, instance, created, **kwargs):
    if not created:
        item_count = instance.items.all().count()
        if item_count == 0:
            instance.delete()
