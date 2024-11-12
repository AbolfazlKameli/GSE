from django.db import transaction
from rest_framework import serializers

from .models import Product, ProductMedia, ProductCategory, ProductDetail
from .selectors import get_primary_image


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'


class ProductMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMedia
        exclude = ('product',)


class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDetail
        exclude = ('product',)


class ProductDetailsSerializer(serializers.ModelSerializer):
    media = ProductMediaSerializer(required=False, many=True, read_only=True)
    details = ProductDetailSerializer(required=False, many=True, read_only=True)
    category = serializers.SlugRelatedField(
        many=True,
        slug_field='title',
        read_only=True
    )

    class Meta:
        model = Product
        fields = '__all__'


class ProductListSerializer(serializers.ModelSerializer):
    media = serializers.SerializerMethodField()
    category = serializers.SlugRelatedField(
        many=True,
        slug_field='title',
        read_only=True
    )

    def get_media(self, obj):
        image = get_primary_image(obj)
        return ProductMediaSerializer(instance=image).data

    class Meta:
        model = Product
        fields = '__all__'


class ProductOperationsSerializer(serializers.ModelSerializer):
    details = ProductDetailSerializer(many=True, write_only=True, required=True)
    media = ProductMediaSerializer(many=True, write_only=True, required=True)
    category = serializers.SlugRelatedField(
        many=True,
        queryset=ProductCategory.objects.all(),
        slug_field='title',
        required=True
    )

    @transaction.atomic
    def create(self, validated_data):
        detail_data = validated_data.pop('details')
        media_data = validated_data.pop('media')
        category_data = validated_data.pop('category')

        product: Product = Product.objects.create(**validated_data)

        for category in category_data:
            product.category.add(category)

        for detail in detail_data:
            ProductDetail.objects.create(product=product, **detail)

        for media in media_data:
            ProductMedia.objects.create(product=product, **media)

        return product

    class Meta:
        model = Product
        exclude = ('slug',)
