from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, DestroyAPIView, ListAPIView, GenericAPIView
from rest_framework.response import Response

from gse.docs.serializers.doc_serializers import ResponseSerializer
from gse.permissions.permissions import IsAdminOrOwner, IsAdminOrSupporter, FullCredentialsUser
from gse.utils.utils import is_child_of, format_errors
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
    """
    API for retrieving the details of an order, accessible only to the order owner or an admin or support.
    """
    serializer_class = OrderSerializer
    queryset = get_all_orders()
    permission_classes = [IsAdminOrOwner]
    lookup_url_kwarg = 'order_id'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response(
            data={'data': response.data},
            status=status.HTTP_200_OK
        )


class UserOrdersListAPI(ListAPIView):
    """
    API for listing all orders of the authenticated user, accessible only to the user or an admin or support.
    """
    permission_classes = [IsAdminOrOwner]
    serializer_class = OrderListSerializer
    filterset_fields = ['status']

    def get_queryset(self) -> list[Order]:
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        return self.request.user.orders.all()


class OrderCreateAPI(GenericAPIView):
    """
    API for creating a new order, accessible only to authenticated users.
    """
    serializer_class = OrderCreateSerializer
    permission_classes = [FullCredentialsUser]

    @extend_schema(responses={201: ResponseSerializer})
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
    """
    API for canceling an order, accessible only to the order owner or an admin or support,
    and only for orders with a 'pending' status.
    """
    permission_classes = [IsAdminOrOwner]
    allowed_statuses = [ORDER_STATUS_PENDING]
    lookup_url_kwarg = 'order_id'

    @extend_schema(responses={200: ResponseSerializer})
    def post(self, request, *args, **kwargs):
        order: Order | None = get_order_by_id(kwargs.get('pk'), check_owner=True, owner=request.user)
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
    """
    API for deleting an item from an order, accessible only to the order owner or an admin or support,
    and only for orders with a 'pending' status.
    """
    permission_classes = [IsAdminOrOwner]
    serializer_class = OrderItemSerializer
    allowed_statuses = [ORDER_STATUS_PENDING]

    def get_object(self):
        order: Order | None = get_order_by_id(self.kwargs.get('order_id'), check_owner=True, owner=self.request.user)
        if order is None or not check_order_status(order, self.allowed_statuses):
            raise Http404({'data': {'errors': 'سفارش درحال پردازشی با این مشخصات پیدا نشد.'}})

        item: OrderItem | None = order.items.filter(id=self.kwargs.get('item_id')).first()
        if item is None or not is_child_of(Order, OrderItem, order.id, item.id):
            raise Http404({'data': {'errors': 'آیتم مربوط به این سفارش با این مشخصات پیدا نشد.'}})

        return item

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        order: Order | None = get_order_by_id(kwargs.get('order_id'), check_owner=True, owner=request.user)
        if order is None or not check_order_status(order, self.allowed_statuses):
            raise Http404({'data': {'errors': 'سفارش درحال پردازشی با این مشخصات پیدا نشد.'}})
        order.remove_if_no_item()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class CouponRetrieveAPI(RetrieveAPIView):
    """
    API for retrieving coupon details, accessible only to admin users.
    """
    serializer_class = CouponSerializer
    queryset = get_all_coupons()
    permission_classes = [IsAdminOrSupporter]
    lookup_url_kwarg = 'coupon_id'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response(
            data={'data': response.data},
            status=response.status_code
        )


class CouponCreateAPI(GenericAPIView):
    """
    API for creating a new coupon, accessible only to admin users.
    """
    serializer_class = CouponSerializer
    permission_classes = [IsAdminOrSupporter]

    @extend_schema(responses={201: ResponseSerializer})
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
    """
    API for updating a coupon, accessible only to admin users.
    """
    serializer_class = CouponSerializer
    permission_classes = [IsAdminOrSupporter]

    @extend_schema(responses={200: ResponseSerializer})
    def patch(self, request, *args, **kwargs):
        coupon_object: Coupon | None = get_coupon_by_id(coupon_id=kwargs.get('coupon_id'))
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
    """
    API for deleting a coupon, accessible only to admin users.
    """
    serializer_class = CouponSerializer
    permission_classes = [IsAdminOrSupporter]
    queryset = get_all_coupons()
    lookup_url_kwarg = 'coupon_id'


class CouponApplyAPI(GenericAPIView):
    """
    API for applying a coupon to a pending order, accessible only to the order owner or an admin or support.
    """
    serializer_class = CouponApplySerializer
    permission_classes = [IsAdminOrOwner]
    allowed_statuses = [ORDER_STATUS_PENDING]

    def get_object(self):
        order_id = self.request.data.get('order_id')
        order: Order | None = get_order_by_id(order_id=order_id, check_owner=False)
        if order is None or not check_order_status(order, self.allowed_statuses):
            raise Http404('سفارش درحال پردازشی با این مشخصات وجود ندارد.')
        self.check_object_permissions(self.request, order)
        return order

    @extend_schema(responses={200: ResponseSerializer})
    def post(self, request, *args, **kwargs):
        self.get_object()
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
    """
    API for discarding a coupon from a pending order, accessible only to the order owner or an admin.
    """
    serializer_class = CouponDiscardSerializer
    permission_classes = [IsAdminOrOwner]
    allowed_statuses = [ORDER_STATUS_PENDING]

    def get_object(self):
        order_id = self.request.data.get('order_id')
        order: Order | None = get_order_by_id(order_id=order_id, check_owner=False)
        if order is None or not check_order_status(order, self.allowed_statuses):
            raise Http404('سفارش درحال پردازشی با این مشخصات وجود ندارد.')
        self.check_object_permissions(self.request, order)
        return order

    @extend_schema(responses={200: ResponseSerializer})
    def post(self, request, *args, **kwargs):
        self.get_object()
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
