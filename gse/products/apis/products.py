from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.response import Response

from gse.utils import format_errors
from gse.utils.doc_serializers import ResponseSerializer
from gse.utils.permissions import IsAdminOrSupporter
from ..models import Product
from ..selectors import get_all_products
from ..serializers import (
    ProductDetailsSerializer,
    ProductListSerializer,
    ProductOperationsSerializer,
    ProductUpdateSerializer
)
from ..services import create_product


@extend_schema(tags=['Products'])
class ProductsListAPI(ListAPIView):
    """
    API for listing all products, with optional filters and search functionality.
    """
    queryset = get_all_products()
    serializer_class = ProductListSerializer
    filterset_fields = ['available']
    search_fields = ['title', 'description', 'slug', 'category__title']


@extend_schema(tags=['Products'])
class ProductRetrieveAPI(RetrieveAPIView):
    """
    API for retrieving the details of a specific product.
    """
    queryset = get_all_products()
    serializer_class = ProductDetailsSerializer
    lookup_url_kwarg = 'product_id'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response(
            data={'data': response.data},
            status=response.status_code
        )


@extend_schema(tags=['Products'])
class ProductCreateAPI(GenericAPIView):
    """
    API for creating a new product, accessible only to admin users.
    """
    serializer_class = ProductOperationsSerializer
    permission_classes = [IsAdminOrSupporter]

    @extend_schema(responses={201: ResponseSerializer})
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            details = serializer.validated_data.pop('details')
            categories = serializer.validated_data.pop('categories')
            create_product(**serializer.validated_data, details=details, categories=categories)
            return Response(
                data={'data': {'message': 'محصول با موفقیت ثبت شد.'}},
                status=status.HTTP_201_CREATED
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(tags=['Products'])
class ProductUpdateAPI(GenericAPIView):
    """
    API for updating an existing product, accessible only to admin users.
    """
    serializer_class = ProductUpdateSerializer
    permission_classes = [IsAdminOrSupporter]
    lookup_url_kwarg = 'product_id'

    @extend_schema(responses={200: ResponseSerializer})
    def patch(self, request, *args, **kwargs):
        product: Product = get_object_or_404(Product, id=kwargs.get('product_id'))
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


@extend_schema(tags=['Products'])
class ProductDestroyAPI(DestroyAPIView):
    """
    API for deleting a product, accessible only to admin users.
    """
    serializer_class = ProductOperationsSerializer
    queryset = get_all_products()
    permission_classes = [IsAdminOrSupporter]
    lookup_url_kwarg = 'product_id'
