from django.http import Http404
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, DestroyAPIView, ListAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from gse.permissions.permissions import IsAdminOrOwner
from gse.utils.db_utils import is_child_of
from gse.utils.format_errors import format_errors
from .choices import ORDER_STATUS_PENDING
from .models import Order, OrderItem, Coupon
from .selectors import (
    get_all_orders,
    get_order_by_id,
    check_order_status,
    get_all_coupons,
    get_coupon_by_id
)
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderItemSerializer,
    OrderListSerializer,
    CouponSerializer,
    CouponApplySerializer,
    CouponDiscardSerializer
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


class OrderCreateAPI(GenericAPIView):
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


class OrderCancelAPI(GenericAPIView):
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
    allowed_statuses = [ORDER_STATUS_PENDING]

    def get_object(self):
        order: Order | None = get_order_by_id(self.kwargs.get('order_id'))
        if order is None or not check_order_status(order, self.allowed_statuses):
            raise Http404({'data': {'errors': 'سفارش درحال پردازشی با این مشخصات پیدا نشد.'}})

        item: OrderItem | None = order.items.filter(id=self.kwargs.get('pk')).first()
        if item is None or not is_child_of(Order, OrderItem, order.id, item.id):
            raise Http404({'data': {'errors': 'آیتم مربوط به این سفارش با این مشخصات پیدا نشد.'}})

        return item

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        order: Order | None = get_order_by_id(kwargs.get('order_id'))
        if order is None or not check_order_status(order, self.allowed_statuses):
            raise Http404({'data': {'errors': 'سفارش درحال پردازشی با این مشخصات پیدا نشد.'}})
        order.remove_if_no_item()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class CouponRetrieveAPI(RetrieveAPIView):
    serializer_class = CouponSerializer
    queryset = get_all_coupons()
    permission_classes = [IsAdminUser]


class CouponCreateAPI(GenericAPIView):
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data={'data': {'message': 'کد تخفیف با موفقیت ثبت شد.'}},
                status=status.HTTP_201_CREATED
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


class CouponUpdateAPI(GenericAPIView):
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUser]

    def patch(self, request, *args, **kwargs):
        coupon_object: Coupon | None = get_coupon_by_id(coupon_id=kwargs.get('pk'))
        if coupon_object is None:
            raise Http404('کد تخفیف با این مشخصات یافت نشد.')
        serializer = self.serializer_class(data=request.data, instance=coupon_object, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data={'data': {'message': 'کد تخفیف با موفقیت ویرایش شد.'}},
                status=status.HTTP_200_OK
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


class CouponDeleteAPI(DestroyAPIView):
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUser]
    queryset = get_all_coupons()


class CouponApplyAPI(GenericAPIView):
    serializer_class = CouponApplySerializer
    permission_classes = [IsAdminOrOwner]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data={'data': {'message': 'کد تخفیف با موفقیت روی سفارش اعمال شد.'}},
                status=status.HTTP_200_OK
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


class CouponDiscardAPI(GenericAPIView):
    serializer_class = CouponDiscardSerializer
    permission_classes = [IsAdminOrOwner]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data={'data': {'message': 'کد تخفیف غیرفعال شد.'}},
                status=status.HTTP_200_OK
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )
