from rest_framework import status
from rest_framework.generics import RetrieveAPIView, DestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from gse.permissions.permissions import IsAdminOrOwner
from gse.utils.format_errors import format_errors
from .choices import ORDER_STATUS_PENDING
from .models import Order
from .selectors import (
    get_all_orders,
    get_all_order_items,
    get_order_by_id,
    check_order_status,
    get_all_coupons
)
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderItemSerializer,
    OrderListSerializer,
    CouponSerializer
)
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


class UserOrdersListAPI(ListAPIView):
    permission_classes = [IsAdminOrOwner]
    serializer_class = OrderListSerializer
    filterset_fields = ['status']

    def get_queryset(self):
        return self.request.user.orders.all()


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
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


class OrderCancelAPI(APIView):
    permission_classes = [IsAdminOrOwner]
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
    permission_classes = [IsAdminOrOwner]
    serializer_class = OrderItemSerializer
    queryset = get_all_order_items()


class CouponRetrieveAPI(RetrieveAPIView):
    serializer_class = CouponSerializer
    queryset = get_all_coupons()
    permission_classes = [IsAdminUser]
