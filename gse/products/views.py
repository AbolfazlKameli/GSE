from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from gse.utils.format_errors import format_errors
from .models import Product
from .selectors import (
    get_all_products
)
from .serializers import (
    ProductDetailsSerializer,
    ProductListSerializer,
    ProductOperationsSerializer,
    ProductUpdateSerializer
)


class ProductsListAPI(ListAPIView):
    """
    List all Product objects.
    """
    queryset = get_all_products()
    serializer_class = ProductListSerializer


class ProductRetrieveAPI(RetrieveAPIView):
    """
    Retrieve a product object.
    """
    queryset = get_all_products()
    serializer_class = ProductDetailsSerializer

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response(
            data={'data': response.data},
            status=response.status_code
        )


class ProductCreateAPI(APIView):
    """
    Creates a Product object.
    """
    serializer_class = ProductOperationsSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data={'data': {'message': 'محصول با موفقیت ثبت شد.'}},
                status=status.HTTP_201_CREATED
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


class ProductUpdateAPI(APIView):
    """
    Updated a Product object.
    """
    serializer_class = ProductUpdateSerializer

    def patch(self, request, *args, **kwargs):
        product: Product | None = get_object_or_404(Product, id=kwargs.get('pk'))
        serializer = self.serializer_class(data=request.data, instance=product, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data={'data': {'message': 'محصول با موفقیت به روز رسانی شد.'}},
                status=status.HTTP_200_OK
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


class ProductDestroyAPI(DestroyAPIView):
    serializer_class = ProductOperationsSerializer
    queryset = get_all_products()
