from rest_framework import status
from rest_framework.generics import RetrieveAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .choices import ORDER_STATUS_PENDING
from .models import Order
from .selectors import get_all_orders, get_all_order_items, get_order_by_id, check_order_status
from .serializers import OrderSerializer, OrderCreateSerializer, OrderItemSerializer
from .services import cancel_order


class OrderRetrieveAPI(RetrieveAPIView):
    serializer_class = OrderSerializer
    queryset = get_all_orders()

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response(
            data={'data': response.data},
            status=status.HTTP_200_OK
        )


class OrderCreateAPI(APIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(
                data={'data': {'message': 'سفارش با موفقیت ایجاد شد.'}},
                status=status.HTTP_201_CREATED
            )
        return Response(
            data={'data': {'errors': serializer.errors}},
            status=status.HTTP_400_BAD_REQUEST
        )


class OrderCancelAPI(APIView):
    permission_classes = [IsAuthenticated]
    allowed_statuses = [ORDER_STATUS_PENDING]

    def post(self, request, *args, **kwargs):
        order: Order | None = get_order_by_id(kwargs.get('pk'))
        if order is None or not check_order_status(order, self.allowed_statuses):
            return Response(
                data={'data': {'errors': 'هیچ سفارش درحال پردازشی یافت نشد.'}},
                status=status.HTTP_404_NOT_FOUND
            )
        cancel_order(order)
        return Response(
            data={'data': {'message': 'سفارش لغو شد.'}},
            status=status.HTTP_200_OK
        )


class OrderItemDeleteAPI(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderItemSerializer
    queryset = get_all_order_items()
