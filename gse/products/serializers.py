from rest_framework import serializers

from .models import Product, ProductMedia, ProductCategory


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'


class ProductMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMedia
        exclude = ('product',)


class ProductListSerializer(serializers.ModelSerializer):
    media = ProductMediaSerializer(required=False, many=True)

    class Meta:
        model = Product
        fields = '__all__'
