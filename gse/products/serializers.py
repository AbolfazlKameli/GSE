from rest_framework import serializers

from .models import Product, ProductMedia, ProductCategory
from .selectors import get_primary_image


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'


class ProductMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMedia
        exclude = ('product',)


class ProductListSerializer(serializers.ModelSerializer):
    media = serializers.SerializerMethodField()

    def get_media(self, obj):
        image = get_primary_image(obj)
        return ProductMediaSerializer(instance=image).data

    class Meta:
        model = Product
        fields = '__all__'
