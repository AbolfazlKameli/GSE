from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .selectors import get_all_tickets
from .serializers import TicketsListSerializer, TicketSerializer


class TicketsListAPI(ListAPIView):
    """
    API for listing tickets, accessible only to admins.
    """
    permission_classes = [IsAdminUser]
    serializer_class = TicketsListSerializer
    queryset = get_all_tickets()
    filterset_fields = ('status',)


class TicketRetrieveAPI(RetrieveAPIView):
    """
    API for retrieving a ticket object.
    """
    serializer_class = TicketSerializer
    queryset = get_all_tickets()

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response(
            data={'data': response.data},
            status=response.status_code
        )
