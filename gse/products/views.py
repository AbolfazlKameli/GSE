from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from gse.docs.serializers.doc_serializers import ResponseSerializer
from gse.utils.db_utils import is_child_of
from gse.utils.format_errors import format_errors
from gse.utils.update_response import update_response
from .models import Product, ProductDetail, ProductMedia
from .selectors import (
    get_all_products,
    get_all_details,
    get_all_media
)
from .serializers import (
    ProductDetailsSerializer,
    ProductListSerializer,
    ProductOperationsSerializer,
    ProductUpdateSerializer,
    ProductDetailSerializer,
    ProductMediaSerializer
)


class ProductsListAPI(ListAPIView):
    """
    List all Product objects.
    """
    queryset = get_all_products()
    serializer_class = ProductListSerializer
    filterset_fields = ['available']
    search_fields = ['title', 'description', 'slug', 'category']


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


class ProductCreateAPI(GenericAPIView):
    """
    Creates a Product object.
    """
    serializer_class = ProductOperationsSerializer
    permission_classes = [IsAdminUser]

    @extend_schema(responses={201: ResponseSerializer})
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


class ProductUpdateAPI(GenericAPIView):
    """
    Updates a Product object.
    """
    serializer_class = ProductUpdateSerializer
    permission_classes = [IsAdminUser]

    @extend_schema(responses={200: ResponseSerializer})
    def patch(self, request, *args, **kwargs):
        product: Product = get_object_or_404(Product, id=kwargs.get('pk'))
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
    permission_classes = [IsAdminUser]


class ProductDetailCreateAPI(GenericAPIView):
    """
    Creates a ProductDetail object.
    """
    serializer_class = ProductDetailSerializer
    permission_classes = [IsAdminUser]

    @extend_schema(responses={201: ResponseSerializer})
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        product: Product = get_object_or_404(Product, id=kwargs.get('pk'))
        if serializer.is_valid():
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
    permission_classes = [IsAdminUser]
    lookup_field = 'id'
    lookup_url_kwarg = 'detail_id'

    @extend_schema(responses={200: ResponseSerializer})
    def patch(self, request, *args, **kwargs):
        if not is_child_of(Product, ProductDetail, kwargs.get('pk'), kwargs.get('detail_id')):
            return Response(
                data={'data': {'errors': 'محصول مرتبط یافت نشد.'}},
                status=status.HTTP_404_NOT_FOUND
            )
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
    permission_classes = [IsAdminUser]
    http_method_names = ['delete', 'options', 'head']
    lookup_field = 'id'
    lookup_url_kwarg = 'detail_id'

    def destroy(self, request, *args, **kwargs):
        if not is_child_of(Product, ProductDetail, kwargs.get('pk'), kwargs.get('detail_id')):
            return Response(
                data={'data': {'errors': 'محصول مرتبط یافت نشد.'}},
                status=status.HTTP_404_NOT_FOUND
            )
        return super().destroy(request, *args, **kwargs)


class ProductMediaCreateAPI(GenericAPIView):
    """
    Creates a ProductMedia object.
    """
    serializer_class = ProductMediaSerializer
    permission_classes = [IsAdminUser]

    @extend_schema(responses={201: ResponseSerializer})
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        product: Product = get_object_or_404(Product, id=kwargs.get('pk'))
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(
                data={'data': {'message': 'رسانه محصول با موفقیت ثبت شد.'}},
                status=status.HTTP_201_CREATED
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


class ProductMediaUpdateAPI(UpdateAPIView):
    """
    Updates a ProductMedia object.
    """
    serializer_class = ProductMediaSerializer
    queryset = get_all_media()
    permission_classes = [IsAdminUser]
    http_method_names = ['patch', 'options', 'head']
    lookup_field = 'id'
    lookup_url_kwarg = 'media_id'

    @extend_schema(responses={200: ResponseSerializer})
    def patch(self, request, *args, **kwargs):
        if not is_child_of(Product, ProductMedia, kwargs.get('pk'), kwargs.get('media_id')):
            return Response(
                data={'data': {'errors': 'محصول مرتبط یافت نشد.'}},
                status=status.HTTP_404_NOT_FOUND
            )
        return update_response(
            super().patch(request, *args, **kwargs),
            "رسانه محصول با موفقیت به روزرسانی شد.",
        )


class ProductMediaDeleteAPI(DestroyAPIView):
    """
    Deletes a ProductMedia object.
    """
    serializer_class = ProductMediaSerializer
    queryset = get_all_media()
    permission_classes = [IsAdminUser]
    http_method_names = ['delete', 'options', 'head']
    lookup_field = 'id'
    lookup_url_kwarg = 'media_id'

    def destroy(self, request, *args, **kwargs):
        if not is_child_of(Product, ProductMedia, kwargs.get('pk'), kwargs.get('media_id')):
            return Response(
                data={'data': {'errors': 'محصول مرتبط یافت نشد.'}},
                status=status.HTTP_404_NOT_FOUND
            )
        return super().destroy(request, *args, **kwargs)
