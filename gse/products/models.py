from django.core.validators import MaxValueValidator
from django.db import models


class ProductCategory(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250)
    is_sub = models.BooleanField(default=False)
    sub_category = models.ForeignKey('self', on_delete=models.CASCADE, related_name='s_category', blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


class Product(models.Model):
    category = models.ManyToManyField(ProductCategory, related_name='products', blank=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250)
    quantity = models.PositiveSmallIntegerField(validators=[MaxValueValidator(1000)])
    description = models.TextField()
    available = models.BooleanField(default=True)
    unit_price = models.DecimalField(max_digits=15, decimal_places=0)
    discount_percent = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)])
    created_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)


class ProductDetail(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='details')
    attribute = models.CharField(max_length=250)
    value = models.CharField(max_length=250)
