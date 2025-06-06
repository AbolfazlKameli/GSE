from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.generics import RetrieveAPIView, DestroyAPIView
from rest_framework.response import Response

from gse.utils import format_errors
from gse.utils.doc_serializers import ResponseSerializer
from gse.utils.permissions import IsAdminOrOwner
from .selectors import get_all_carts, get_all_cart_items, get_cart_by_item_id, get_cart_item_by_id
from .serializers import CartSerializer, CartItemAddSerializer, CartItemSerializer
from .services import add_cart_item


class CartRetrieveAPI(RetrieveAPIView):
    """
    API for retrieving the authenticated user's cart details, accessible only to the cart owner or an admin or support.
    """
    serializer_class = CartSerializer
    queryset = get_all_carts()
    permission_classes = [IsAdminOrOwner]

    def get_object(self):
        return self.request.user.cart

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response(
            data={'data': response.data},
            status=status.HTTP_200_OK
        )


class CartItemAddAPI(GenericAPIView):
    """
    API for adding an item to the authenticated user's cart, accessible only to the cart owner or an admin or support.
    """
    serializer_class = CartItemAddSerializer
    permission_classes = [IsAdminOrOwner]

    @extend_schema(responses={201: ResponseSerializer})
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            add_cart_item(request.user.cart, serializer.validated_data)
            return Response(
                data={'data': {'message': 'محصول با موفقیت به سبد خرید اضافه شد.'}},
                status=status.HTTP_201_CREATED
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


class CartItemDeleteAPI(DestroyAPIView):
    """
    API for deleting an item from the authenticated user's cart,
    accessible only to the cart owner or an admin or support.
    """
    serializer_class = CartItemSerializer
    permission_classes = [IsAdminOrOwner]
    queryset = get_all_cart_items()

    def get_object(self):
        item_id = self.kwargs.get('item_id')
        cart = get_cart_by_item_id(item_id=item_id)
        self.check_object_permissions(self.request, cart)
        return cart

    def delete(self, request, *args, **kwargs):
        cart_item = get_cart_item_by_id(item_id=kwargs.get('item_id'))
        if cart_item is None:
            raise Http404('آیتم مورد نظر پیدا نشد.')
        cart_item.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
