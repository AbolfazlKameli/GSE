from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from .serializers import OrderSerializer
from .selectors import get_all_orders


class OrderRetrieveAPI(RetrieveAPIView):
    serializer_class = OrderSerializer
    queryset = get_all_orders()

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response(
            data={'data': response.data},
            status=status.HTTP_200_OK
        )
