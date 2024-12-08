from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser

from .selectors import get_all_tickets
from .serializers import TicketsListSerializer


class TicketsListAPI(ListAPIView):
    """
    API for listing tickets, accessible only to admins.
    """
    permission_classes = [IsAdminUser]
    serializer_class = TicketsListSerializer
    queryset = get_all_tickets()
    filterset_fields = ('status',)
