from rest_framework.generics import ListAPIView

from .models import Product
from .serializers import ProductListSerializer


class ProductsListAPI(ListAPIView):
    """
    List all Product objects.
    """
    queryset = Product.objects.prefetch_related('details', 'media').all()
    serializer_class = ProductListSerializer
