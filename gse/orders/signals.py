from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import Order


@receiver(post_save, sender=Order)
def check_order_item_count(sender, instance, created, **kwargs):
    if not created:
        item_count = instance.items.all().count()
        if item_count == 0:
            instance.delete()


@receiver(pre_delete, sender=Order)
def check_coupon_usage_limit(sender, instance, **kwargs):
    if instance.coupon is not None:
        instance.coupon.max_usage_limit += 1
        instance.coupon.save()
