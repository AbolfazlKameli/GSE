from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.core.validators import FileExtensionValidator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg

from .choices import MEDIA_TYPE_CHOICES, MEDIA_TYPE_IMAGE, MEDIA_TYPE_VIDEO
from .services import slugify_title
from .validators import VideoDurationValidator
from ..users.models import User


class ProductCategory(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, allow_unicode=True)
    is_sub = models.BooleanField(default=False, db_index=True)
    sub_category = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='s_category',
        blank=True,
        null=True,
        db_index=True
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify_title(self.title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'categories'


class Product(models.Model):
    category = models.ManyToManyField(ProductCategory, related_name='products', blank=True, db_index=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, allow_unicode=True)
    quantity = models.PositiveSmallIntegerField(validators=[MaxValueValidator(1000)], db_index=True)
    description = models.TextField()
    available = models.BooleanField(default=True, db_index=True)
    unit_price = models.DecimalField(
        validators=[MinValueValidator(Decimal(0))],
        max_digits=15,
        decimal_places=0,
        db_index=True
    )
    discount_percent = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)], default=0, db_index=True)
    final_price = models.DecimalField(
        validators=[MinValueValidator(Decimal(0))],
        max_digits=15,
        decimal_places=0,
        default=0,
        db_index=True
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify_title(self.title)
        self.final_price = self.get_price()
        if self.quantity == 0:
            self.available = False
        super().save(*args, **kwargs)

    @property
    def overall_rate(self):
        avg_rate = self.reviews.aggregate(avg=Avg('rate'))['avg']
        return round(avg_rate, 1) if avg_rate is not None else 0

    def get_price(self):
        if self.discount_percent > 0:
            discount_amount = self.unit_price * Decimal(self.discount_percent / 100)
            discounted_amount = self.unit_price - discount_amount
            return round(discounted_amount)
        else:
            return round(self.unit_price)

    class Meta:
        ordering = ('-created_date',)


class ProductDetail(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='details', db_index=True)
    attribute = models.CharField(max_length=250)
    value = models.CharField(max_length=250)


class ProductMedia(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='media', db_index=True)
    media_type = models.CharField(
        choices=MEDIA_TYPE_CHOICES,
        verbose_name='نوع رسانه',
        max_length=10,
        db_index=True
    )
    media_url = models.FileField(validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'mp4', 'gif'])])
    is_primary = models.BooleanField(default=False, db_index=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.media_type == MEDIA_TYPE_IMAGE and not self.media_url.name.lower().endswith(
                ('png', 'jpg', 'jpeg')):
            raise ValidationError('اگر نوع رسانه عکس انتخاب شده، فایل آپلود شده باید عکس باشد.')

        if self.media_type == MEDIA_TYPE_VIDEO and not self.media_url.name.lower().endswith(('.mp4', '.mov', '.avi')):
            raise ValidationError("اگر نوع رسانه ویدیو انتخاب شده، فایل آپلود شده باید ویدیو باشد.")

        if self.media_type == MEDIA_TYPE_VIDEO and self.is_primary:
            raise ValidationError("ویدیو نمیتواند به عنوان رسانه اصلی استفاده شود.")

        if self.media_type == MEDIA_TYPE_IMAGE:
            h, w = get_image_dimensions(self.media_url)
            if not 900 <= w <= 1000:
                raise ValidationError('عرض عکس باید بین ۹۰۰ تا ۱۰۰۰ پیکسل باشد.')

            if not 900 <= h <= 1000:
                raise ValidationError('طول عکس باید بین ۹۰۰ تا ۱۰۰۰ پیکسل باشد.')

        if self.media_type == MEDIA_TYPE_VIDEO:
            validator = VideoDurationValidator(max_duration=600)
            validator(self.media_url)

        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', db_index=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', db_index=True)
    body = models.CharField(max_length=255)
    rate = models.PositiveSmallIntegerField(validators=[MaxValueValidator(5)], db_index=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
