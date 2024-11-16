from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from .selectors import get_all_carts
from .serializers import (
    CartSerializer
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
