from .choices import MEDIA_TYPE_IMAGE
from .models import Product, ProductMedia, ProductDetail, ProductCategory, ProductReview


def get_sub_categories(parent_id: int) -> list[ProductCategory]:
    return ProductCategory.objects.filter(is_sub=True, sub_category=parent_id)


def get_parent_categories() -> list[ProductCategory]:
    return ProductCategory.objects.filter(is_sub=False)


def get_all_categories() -> list[ProductCategory]:
    return ProductCategory.objects.all()


def get_primary_image(product: Product) -> ProductMedia:
    media: ProductMedia | None = product.media.filter(is_primary=True, media_type=MEDIA_TYPE_IMAGE).first()
    if media is None:
        return product.media.filter(media_type=MEDIA_TYPE_IMAGE).first()
    return media


def get_all_products() -> list[Product]:
    return Product.objects.prefetch_related('media', 'details', 'category').all()


def get_product_by_id(product_id: int) -> list[Product]:
    return Product.objects.prefetch_related('questions').filter(id=product_id).first()


def get_products_for_update_by_ids(product_ids: list[int]) -> dict[int, Product]:
    return Product.objects.filter(id__in=product_ids).select_for_update().in_bulk()


def get_all_details() -> list[ProductDetail]:
    return ProductDetail.objects.select_related('product').all()


def get_all_media() -> list[ProductMedia]:
    return ProductMedia.objects.select_related('product').all()


def get_product_reviews(product: Product) -> list[ProductReview]:
    return ProductReview.objects.filter(product__exact=product)


def get_all_reviews() -> list[ProductReview]:
    return ProductReview.objects.all()


def get_review_by_id(review_id: int) -> ProductReview:
    return ProductReview.objects.filter(id=review_id).first()
