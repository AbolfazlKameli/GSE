from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response

from .models import Product
from .serializers import (
    ProductDetailsSerializer,
    ProductListSerializer
)


class ProductsListAPI(ListAPIView):
    """
    List all Product objects.
    """
    queryset = Product.objects.prefetch_related('details', 'media').all()
    serializer_class = ProductListSerializer


class ProductRetrieveAPI(RetrieveAPIView):
    """
    Retrieve a product object
    """
    queryset = Product.objects.prefetch_related('details', 'media').all()
    serializer_class = ProductDetailsSerializer

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response(
            data={'data': response.data},
            status=response.status_code
        )
