from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from gse.utils.format_errors import format_errors
from .selectors import (
    get_all_products
)
from .serializers import (
    ProductDetailsSerializer,
    ProductListSerializer,
    ProductCreateSerializer
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
    serializer_class = ProductCreateSerializer
    queryset = get_all_products()

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
