from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from gse.utils.format_errors import format_errors
from gse.utils.update_response import update_response
from .models import Product
from .selectors import (
    get_all_products,
    get_all_details
)
from .serializers import (
    ProductDetailsSerializer,
    ProductListSerializer,
    ProductOperationsSerializer,
    ProductUpdateSerializer,
    ProductDetailSerializer
)


class ProductsListAPI(ListAPIView):
    """
    List all Product objects.
    """
    queryset = get_all_products()
    serializer_class = ProductListSerializer


class ProductRetrieveAPI(RetrieveAPIView):
    """
    Retrieves a product object.
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
    Updates a Product object.
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
    """
    Deletes a Product object.
    """
    serializer_class = ProductOperationsSerializer
    queryset = get_all_products()


class ProductDetailCreateAPI(APIView):
    """
    Creates a ProductDetail object.
    """
    serializer_class = ProductDetailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            product: Product | None = Product.objects.filter(id=kwargs.get('pk')).first()
            serializer.save(product=product)
            return Response(
                data={'data': {'message': 'جزییات محصول با موفقیت ثبت شد.'}},
                status=status.HTTP_201_CREATED
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


class ProductDetailUpdateAPI(UpdateAPIView):
    """
    Updates a Detail object.
    """
    serializer_class = ProductDetailSerializer
    queryset = get_all_details()
    http_method_names = ['patch', 'options', 'head']
    lookup_field = 'id'
    lookup_url_kwarg = 'detail_id'

    def patch(self, request, *args, **kwargs):
        return update_response(
            super().patch(request, *args, **kwargs),
            "جزییات محصول با موفقیت به روزرسانی شد.",
        )


class ProductDetailDeleteAPI(DestroyAPIView):
    """
    Deletes a Detail object.
    """
    serializer_class = ProductDetailSerializer
    queryset = get_all_details()
    http_method_names = ['delete', 'options', 'head']
    lookup_field = 'id'
    lookup_url_kwarg = 'detail_id'
