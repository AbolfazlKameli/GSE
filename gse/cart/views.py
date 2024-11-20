from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from gse.docs.serializers.doc_serializers import ResponseSerializer
from gse.utils.format_errors import format_errors
from .selectors import get_all_carts, get_all_cart_items
from .serializers import (
    CartSerializer,
    CartItemAddSerializer,
    CartItemSerializer
)


class CartRetrieveAPI(RetrieveAPIView):
    serializer_class = CartSerializer
    queryset = get_all_carts()

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response(
            data={'data': response.data},
            status=status.HTTP_200_OK
        )


class CartItemAddAPI(APIView):
    serializer_class = CartItemAddSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={201: ResponseSerializer})
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(cart=request.user.cart)
            return Response(
                data={'data': {'message': 'محصول با موفقیت به سبد خرید اضافه شد.'}},
                status=status.HTTP_201_CREATED
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


class CartItemDeleteAPI(DestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    queryset = get_all_cart_items()
