from .models import Product, ProductMedia

from .choices import MEDIA_TYPE_IMAGE


def get_primary_image(product: Product) -> ProductMedia:
    media: ProductMedia | None = product.media.filter(is_primary=True, media_type=MEDIA_TYPE_IMAGE).first()
    if media is None:
        return product.media.filter(media_type=MEDIA_TYPE_IMAGE).first()
    return media
