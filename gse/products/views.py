from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from gse.orders.selectors import has_purchased
from gse.utils import is_child_of, format_errors, update_response
from gse.utils.doc_serializers import ResponseSerializer
from gse.utils.permissions import IsAdminOrOwner, IsAdminOrSupporter
from .models import Product, ProductDetail, ProductMedia, ProductCategory, ProductReview
from .selectors import (
    get_all_products,
    get_all_details,
    get_all_media,
    get_parent_categories,
    get_all_categories,
    get_product_reviews,
    get_review_by_id,
    get_all_reviews
)
from .serializers import (
    ProductDetailsSerializer,
    ProductListSerializer,
    ProductOperationsSerializer,
    ProductUpdateSerializer,
    ProductDetailSerializer,
    ProductMediaSerializer,
    ProductCategoryWriteSerializer,
    ProductCategoryReadSerializer,
    ProductReviewSerializer
)


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


class CategoryDeleteAPI(DestroyAPIView):
    """
    API for deleting categories, accessible only to admin users.
    """
    queryset = get_all_categories()
    permission_classes = [IsAdminOrSupporter]
    serializer_class = ProductCategoryWriteSerializer
    lookup_url_kwarg = 'category_id'


class CategoriesListAPI(ListAPIView):
    """
    API for listing all categories.
    """
    queryset = get_parent_categories()
    serializer_class = ProductCategoryReadSerializer
    search_fields = ['title']


class CategoryRetrieveAPI(RetrieveAPIView):
    """
    API for retrieving a category details.
    """
    queryset = get_all_categories()
    serializer_class = ProductCategoryReadSerializer
    lookup_url_kwarg = 'category_id'


class ProductsListAPI(ListAPIView):
    """
    API for listing all products, with optional filters and search functionality.
    """
    queryset = get_all_products()
    serializer_class = ProductListSerializer
    filterset_fields = ['available']
    search_fields = ['title', 'description', 'slug', 'category__title']


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


class ProductDestroyAPI(DestroyAPIView):
    """
    API for deleting a product, accessible only to admin users.
    """
    serializer_class = ProductOperationsSerializer
    queryset = get_all_products()
    permission_classes = [IsAdminOrSupporter]
    lookup_url_kwarg = 'product_id'


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


class ProductMediaCreateAPI(GenericAPIView):
    """
    API for creating product media, accessible only to admin users.
    """
    serializer_class = ProductMediaSerializer
    permission_classes = [IsAdminOrSupporter]

    @extend_schema(responses={201: ResponseSerializer})
    def post(self, request, *args, **kwargs):
        product: Product = get_object_or_404(Product, id=kwargs.get('product_id'))
        serializer = self.serializer_class(data=request.data, context={'product': product})
        if serializer.is_valid():
            serializer.save()
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
    API for updating product media, accessible only to admin users.
    """
    serializer_class = ProductMediaSerializer
    queryset = get_all_media()
    permission_classes = [IsAdminOrSupporter]
    http_method_names = ['patch', 'options', 'head']
    lookup_field = 'id'
    lookup_url_kwarg = 'media_id'

    @extend_schema(responses={200: ResponseSerializer})
    def patch(self, request, *args, **kwargs):
        if not is_child_of(Product, ProductMedia, kwargs.get('product_id'), kwargs.get('media_id')):
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
    API for deleting product media, accessible only to admin users.
    """
    serializer_class = ProductMediaSerializer
    queryset = get_all_media()
    permission_classes = [IsAdminOrSupporter]
    http_method_names = ['delete', 'options', 'head']
    lookup_field = 'id'
    lookup_url_kwarg = 'media_id'

    def destroy(self, request, *args, **kwargs):
        if not is_child_of(Product, ProductMedia, kwargs.get('product_id'), kwargs.get('media_id')):
            return Response(
                data={'data': {'errors': 'محصول مرتبط یافت نشد.'}},
                status=status.HTTP_404_NOT_FOUND
            )
        return super().destroy(request, *args, **kwargs)


class ProductReviewListAPI(ListAPIView):
    """
    API for listing product reviews.
    """
    serializer_class = ProductReviewSerializer
    filterset_fields = ['rate']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ProductReview.objects.none()
        product = get_object_or_404(Product, id=self.kwargs.get('product_id'))
        return get_product_reviews(product=product)


class ProductReviewRetrieve(RetrieveAPIView):
    """
    API for retrieving reviews.
    """
    serializer_class = ProductReviewSerializer
    queryset = get_all_reviews()
    lookup_url_kwarg = 'review_id'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response(
            data={'data': response.data},
            status=response.status_code
        )


class ProductReviewCreateAPI(GenericAPIView):
    """
    API for creating reviews, accessible only to users bought the product.
    """
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={201: ResponseSerializer})
    def post(self, request, *args, **kwargs):
        product: Product = get_object_or_404(Product, id=kwargs.get('product_id'))
        if has_purchased(user=request.user, product=product):
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save(product=product, owner=request.user)
                return Response(
                    data={'data': {'message': 'نظر با موفقیت ثبت شد.'}},
                    status=status.HTTP_201_CREATED
                )
            return Response(
                data={'data': {'errors': format_errors(serializer.errors)}},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            data={'data': {'errors': 'فقط افرادی که این محصول را خریده اند میتوانند نظر ثبت کنند.'}},
            status=status.HTTP_403_FORBIDDEN
        )


class ProductReviewDeleteAPI(DestroyAPIView):
    """
    API for deleting a review, accessible only to user or admin or supporter.
    """
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAdminOrOwner]
    queryset = get_all_reviews()

    def get_object(self):
        if is_child_of(Product, ProductReview, self.kwargs.get('product_id'), self.kwargs.get('review_id')):
            review = get_review_by_id(review_id=self.kwargs.get('review_id'))
            self.check_object_permissions(self.request, review)
            return review
        raise Http404('منیع مورد نظر پیدا نشد.')
