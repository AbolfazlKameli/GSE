from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import DestroyAPIView, UpdateAPIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from gse.utils import is_child_of, format_errors, update_response
from gse.utils.doc_serializers import ResponseSerializer
from gse.utils.permissions import IsAdminOrSupporter
from ..models import Product, ProductDetail
from ..selectors import get_all_details
from ..serializers import ProductDetailSerializer


@extend_schema(tags=['ProductDetails'])
class ProductDetailCreateAPI(GenericAPIView):
    """
    API for creating product details, accessible only to admin users.
    """
    serializer_class = ProductDetailSerializer
    permission_classes = [IsAdminOrSupporter]

    @extend_schema(responses={201: ResponseSerializer})
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        product: Product = get_object_or_404(Product, id=kwargs.get('product_id'))
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


@extend_schema(tags=['ProductDetails'])
class ProductDetailUpdateAPI(UpdateAPIView):
    """
    API for updating product details, accessible only to admin users.
    """
    serializer_class = ProductDetailSerializer
    queryset = get_all_details()
    http_method_names = ['patch', 'options', 'head']
    permission_classes = [IsAdminOrSupporter]
    lookup_field = 'id'
    lookup_url_kwarg = 'detail_id'

    @extend_schema(responses={200: ResponseSerializer})
    def patch(self, request, *args, **kwargs):
        if not is_child_of(Product, ProductDetail, kwargs.get('product_id'), kwargs.get('detail_id')):
            return Response(
                data={'data': {'errors': 'محصول مرتبط یافت نشد.'}},
                status=status.HTTP_404_NOT_FOUND
            )
        return update_response(
            super().patch(request, *args, **kwargs),
            "جزییات محصول با موفقیت به روزرسانی شد.",
        )


@extend_schema(tags=['ProductDetails'])
class ProductDetailDeleteAPI(DestroyAPIView):
    """
    API for deleting product details, accessible only to admin users.
    """
    serializer_class = ProductDetailSerializer
    queryset = get_all_details()
    permission_classes = [IsAdminOrSupporter]
    http_method_names = ['delete', 'options', 'head']
    lookup_field = 'id'
    lookup_url_kwarg = 'detail_id'

    def destroy(self, request, *args, **kwargs):
        if not is_child_of(Product, ProductDetail, kwargs.get('product_id'), kwargs.get('detail_id')):
            return Response(
                data={'data': {'errors': 'محصول مرتبط یافت نشد.'}},
                status=status.HTTP_404_NOT_FOUND
            )
        return super().destroy(request, *args, **kwargs)
