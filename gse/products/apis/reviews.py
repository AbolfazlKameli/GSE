from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from gse.orders.selectors import has_purchased
from gse.utils import is_child_of, format_errors
from gse.utils.doc_serializers import ResponseSerializer
from gse.utils.permissions import IsAdminOrOwner
from ..models import Product, ProductReview
from ..selectors import get_product_reviews, get_review_by_id, get_all_reviews
from ..serializers import ProductReviewSerializer


@extend_schema(tags=['ProductReviews'])
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


@extend_schema(tags=['ProductReviews'])
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


@extend_schema(tags=['ProductReviews'])
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


@extend_schema(tags=['ProductReviews'])
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
