from django.db import models


class ProductCategory(models.Model):
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=250)
    is_sub = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
