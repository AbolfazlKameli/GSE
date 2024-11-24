from django.core.files.images import get_image_dimensions
from django.db import transaction
from rest_framework import serializers

from .choices import MEDIA_TYPE_IMAGE, MEDIA_TYPE_VIDEO
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

    def validate(self, attrs):
        media_type = attrs.get('media_type')
        is_primary = attrs.get('is_primary')
        media_url = attrs.get('media_url')
        max_media_size = 500 * 1024 * 1024

        if media_type == MEDIA_TYPE_IMAGE and not media_url.name.lower().endswith(('png', 'jpg', 'jpeg')):
            raise serializers.ValidationError('اگر نوع رسانه عکس انتخاب شده، فایل آپلود شده باید عکس باشد.')

        if media_type == MEDIA_TYPE_VIDEO and not media_url.name.lower().endswith(('.mp4', '.mov', '.avi')):
            raise serializers.ValidationError("اگر نوع رسانه ویدیو انتخاب شده، فایل آپلود شده باید ویدیو باشد.")

        if media_type == MEDIA_TYPE_IMAGE:
            h, w = get_image_dimensions(media_url)
            if not 900 <= w <= 1000:
                raise serializers.ValidationError('عرض عکس باید بین ۹۰۰ تا ۱۰۰۰ پیکسل باشد.')

            if not 900 <= h <= 1000:
                raise serializers.ValidationError('طول عکس باید بین ۹۰۰ تا ۱۰۰۰ پیکسل باشد.')

        if media_url.size > max_media_size:
            raise serializers.ValidationError('حجم فایل باید کمتر از ۵۰۰ مگابایت باشد.')

        if media_type == MEDIA_TYPE_VIDEO and is_primary:
            raise serializers.ValidationError("ویدیو نمیتواند به عنوان رسانه اصلی استفاده شود.")

        return attrs


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
    media = serializers.SerializerMethodField(read_only=True)
    category = serializers.SlugRelatedField(
        many=True,
        slug_field='title',
        read_only=True
    )

    def get_media(self, obj) -> ProductMediaSerializer:
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

        details = [ProductDetail(product=product, **detail) for detail in detail_data]
        ProductDetail.objects.bulk_create(details)

        media = [ProductMedia(product=product, **media) for media in media_data]
        ProductMedia.objects.bulk_create(media)

        return product

    class Meta:
        model = Product
        exclude = ('slug',)


class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
