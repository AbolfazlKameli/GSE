from django.core.files.images import get_image_dimensions
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .choices import MEDIA_TYPE_IMAGE, MEDIA_TYPE_VIDEO
from .models import Product, ProductMedia, ProductCategory, ProductDetail, ProductReview
from .selectors import get_primary_image, get_parent_categories, get_sub_categories
from .tasks import upload
from .validators import VideoDurationValidator, validate_file_type


class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = '__all__'
        read_only_fields = ('product', 'owner')


class ProductCategoryWriteSerializer(serializers.ModelSerializer):
    sub_category = serializers.PrimaryKeyRelatedField(
        required=False,
        queryset=get_parent_categories(),
    )

    class Meta:
        model = ProductCategory
        fields = '__all__'
        extra_kwargs = {
            'slug': {'required': False},
            'is_sub': {'required': True},
        }

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError('هیچ اطلاعاتی ارسال نشده.')
        is_sub: bool = attrs.get('is_sub')
        sub_category = attrs.get('sub_category')
        if is_sub and not sub_category:
            raise serializers.ValidationError({'sub_category': 'این فیلد الزامی است.'})
        return super().validate(attrs)


class ProductCategoryReadSerializer(serializers.ModelSerializer):
    sub_categories = serializers.SerializerMethodField(read_only=True)

    @extend_schema_field(ProductCategoryWriteSerializer(many=True))
    def get_sub_categories(self, obj):
        sub_categories = get_sub_categories(obj.id)
        return ProductCategoryWriteSerializer(sub_categories, many=True).data

    class Meta:
        model = ProductCategory
        fields = '__all__'


class ProductMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMedia
        exclude = ('product',)
        read_only_fields = ('media_type',)

    def validate(self, attrs):
        allowed_types = {
            'images': ['image/jpeg', 'image/png', 'image/jpg'],
            'videos': ['video/mp4']
        }
        is_primary = attrs.get('is_primary')
        media = attrs.get('media')
        max_media_size = 500 * 1024 * 1024
        media_type = validate_file_type(media, allowed_types)

        if media_type is None:
            raise serializers.ValidationError({'media': 'نوع رسانه مجاز نمیباشد.'})

        if media_type == MEDIA_TYPE_IMAGE and not media.name.lower().endswith(('png', 'jpg', 'jpeg')):
            raise serializers.ValidationError('اگر نوع رسانه عکس انتخاب شده، فایل آپلود شده باید عکس باشد.')

        if media_type == MEDIA_TYPE_VIDEO and not media.name.lower().endswith(('.mp4',)):
            raise serializers.ValidationError("اگر نوع رسانه ویدیو انتخاب شده، فایل آپلود شده باید ویدیو باشد.")

        if media_type == MEDIA_TYPE_IMAGE:
            h, w = get_image_dimensions(media)
            if not 900 <= w <= 1000:
                raise serializers.ValidationError('عرض عکس باید بین ۹۰۰ تا ۱۰۰۰ پیکسل باشد.')

            if not 900 <= h <= 1000:
                raise serializers.ValidationError('طول عکس باید بین ۹۰۰ تا ۱۰۰۰ پیکسل باشد.')

        if media.size > max_media_size:
            raise serializers.ValidationError('حجم فایل باید کمتر از ۵۰۰ مگابایت باشد.')

        if media_type == MEDIA_TYPE_VIDEO and is_primary:
            raise serializers.ValidationError("ویدیو نمیتواند به عنوان رسانه اصلی استفاده شود.")

        if media_type == MEDIA_TYPE_VIDEO:
            validator = VideoDurationValidator(max_duration=600)
            validator(media)

        attrs['media_type'] = media_type
        return attrs

    def create(self, validated_data):
        product = self.context['product']
        media = validated_data.get('media')
        storage = FileSystemStorage()
        storage.save(media.name, media)
        result = upload.delay(product=product, path=storage.path(media.name), file_name=media.name)
        if not result:
            raise serializers.ValidationError('خطای آپلود')
        return result['instance']


class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDetail
        exclude = ('product',)


class ProductDetailsSerializer(serializers.ModelSerializer):
    media = ProductMediaSerializer(required=False, many=True, read_only=True)
    details = ProductDetailSerializer(required=False, many=True, read_only=True)
    reviews = ProductReviewSerializer(required=False, many=True, read_only=True)
    overall_rate = serializers.SerializerMethodField(read_only=True)
    category = serializers.SlugRelatedField(
        many=True,
        slug_field='title',
        read_only=True
    )

    def get_overall_rate(self, obj) -> float:
        return obj.overall_rate

    class Meta:
        model = Product
        fields = '__all__'


class ProductListSerializer(serializers.ModelSerializer):
    media = serializers.SerializerMethodField(read_only=True)
    overall_rate = serializers.SerializerMethodField(read_only=True)
    category = serializers.SlugRelatedField(
        many=True,
        slug_field='title',
        read_only=True
    )

    def get_overall_rate(self, obj) -> float:
        return obj.overall_rate

    def get_media(self, obj) -> ProductMediaSerializer:
        image = get_primary_image(obj)
        return ProductMediaSerializer(instance=image).data

    class Meta:
        model = Product
        fields = '__all__'


class ProductOperationsSerializer(serializers.ModelSerializer):
    details = ProductDetailSerializer(many=True, write_only=True, required=True)
    category = serializers.SlugRelatedField(
        many=True,
        queryset=ProductCategory.objects.all(),
        slug_field='title',
        required=True
    )

    @transaction.atomic
    def create(self, validated_data):
        detail_data = validated_data.pop('details')
        category_data = validated_data.pop('category')

        product: Product = Product.objects.create(**validated_data)

        for category in category_data:
            product.category.add(category)

        details = [ProductDetail(product=product, **detail) for detail in detail_data]
        ProductDetail.objects.bulk_create(details)

        return product

    class Meta:
        model = Product
        exclude = ('slug',)
        read_only_fields = ('final_price',)


class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('final_price',)
