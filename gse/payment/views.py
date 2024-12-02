from django.http import Http404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from gse.orders.choices import ORDER_STATUS_PENDING
from gse.orders.models import Order
from gse.orders.selectors import get_order_by_id, check_order_status, get_pending_orders
from gse.permissions.permissions import IsAdminOrOwner, FullCredentialsUser
from .models import Payment
from .selectors import get_payment_by_id
from .serializer import PaymentSerializer
from .services import payment_request, verify


class ZPPaymentAPI(GenericAPIView):
    """
    API for pay a pending order, accessible only to the user or admin or support.
    """
    allowed_statuses = [ORDER_STATUS_PENDING]
    permission_classes = [IsAdminOrOwner, FullCredentialsUser]
    queryset = get_pending_orders()
    lookup_field = 'id'
    lookup_url_kwarg = 'order_id'

    def get(self, request, *args, **kwargs):
        order: Order = self.get_object()

        response = payment_request(
            amount=order.total_price,
            phone=request.user.profile.phone_number,
            email=request.user.email
        )
        if response.get('code') == 200:
            return Response(
                data={'data': {'url': response.get('url')}},
                status=status.HTTP_202_ACCEPTED
            )
        return Response(
            data={
                'data': {
                    'error': {
                        str(response.get('ErrorName')): response.get('Error'),
                    }
                }
            },
            status=response.get('code')
        )


class ZPVerifyAPI(GenericAPIView):
    """
    API for verifying a payment info, accessible only to the user or admin or support.
    """
    allowed_statuses = [ORDER_STATUS_PENDING]
    permission_classes = [IsAuthenticated, FullCredentialsUser]

    def get_object(self):
        order_id = self.request.query_params.get('order_id')
        order: Order | None = get_order_by_id(order_id, check_owner=True, owner=self.request.user)
        if order is None or not check_order_status(order, self.allowed_statuses):
            raise Http404('سفارش درحال پردازشی با این مشخصات پیدا نشد.')
        return order

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='order_id',
                description='id of a pending order.',
                required=True,
                type=int
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        order: Order = self.get_object()
        amount = order.total_price
        response = verify(request.query_params.get('Status'), request.query_params.get('Authority'), amount, order)
        if response.get('code') == 200:
            return Response(
                data={'data': {'message': response.get('message')}},
                status=status.HTTP_200_OK
            )
        return Response(
            data={'data': {'errors': response}},
            status=response.get('code')
        )


class PaymentReceiptAPI(RetrieveAPIView):
    permission_classes = [IsAdminOrOwner, FullCredentialsUser]
    serializer_class = PaymentSerializer
    lookup_url_kwarg = 'payment_id'
    lookup_field = 'id'

    def get_object(self):
        payment: Payment | None = get_payment_by_id(payment_id=self.kwargs.get('payment_id'))
        if payment is None:
            raise Http404('تراکنشی با این مشخصات وجود ندارد.')
        order = payment.order

        self.check_object_permissions(self.request, order)

        return payment
