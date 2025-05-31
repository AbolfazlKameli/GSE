from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.response import Response

from gse.utils import format_errors
from gse.utils.doc_serializers import ResponseSerializer
from gse.utils.permissions import IsAdminOrSupporter
from ..models import ProductCategory
from ..selectors import get_parent_categories, get_all_categories
from ..serializers import ProductCategoryWriteSerializer, ProductCategoryReadSerializer


@extend_schema(tags=['ProductCategories'])
class CategoryCreateAPI(GenericAPIView):
    """
    API for creating categories, accessible only to admin users.
    """
    permission_classes = [IsAdminOrSupporter]
    serializer_class = ProductCategoryWriteSerializer

    @extend_schema(responses={201: ResponseSerializer})
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data={'data': {'message': 'دسته بندی محصول ایجاد شد.'}},
                status=status.HTTP_201_CREATED
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(tags=['ProductCategories'])
class CategoryUpdateAPI(GenericAPIView):
    """
    API for updating categories, accessible only to admin users.
    """
    queryset = get_all_categories()
    permission_classes = [IsAdminOrSupporter]
    serializer_class = ProductCategoryWriteSerializer
    http_method_names = ['patch', 'options', 'head']
    lookup_url_kwarg = 'category_id'

    @extend_schema(responses={200: ResponseSerializer})
    def patch(self, request, *args, **kwargs):
        category: ProductCategory = get_object_or_404(ProductCategory, id=kwargs.get('category_id'))
        serializer = self.serializer_class(instance=category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data={'data': {'message': 'دسته بندی به روزرسانی شد.'}},
                status=status.HTTP_200_OK
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(tags=['ProductCategories'])
class CategoryDeleteAPI(DestroyAPIView):
    """
    API for deleting categories, accessible only to admin users.
    """
    queryset = get_all_categories()
    permission_classes = [IsAdminOrSupporter]
    serializer_class = ProductCategoryWriteSerializer
    lookup_url_kwarg = 'category_id'


@extend_schema(tags=['ProductCategories'])
class CategoriesListAPI(ListAPIView):
    """
    API for listing all categories.
    """
    queryset = get_parent_categories()
    serializer_class = ProductCategoryReadSerializer
    search_fields = ['title']


@extend_schema(tags=['ProductCategories'])
class CategoryRetrieveAPI(RetrieveAPIView):
    """
    API for retrieving a category details.
    """
    queryset = get_all_categories()
    serializer_class = ProductCategoryReadSerializer
    lookup_url_kwarg = 'category_id'
