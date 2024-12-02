from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from gse.orders.choices import ORDER_STATUS_PENDING
from gse.orders.models import Order
from gse.orders.selectors import get_pending_orders
from gse.permissions.permissions import IsAdminOrOwner, FullCredentialsUser
from .services import payment_request


class ZPPaymentAPI(GenericAPIView):
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
