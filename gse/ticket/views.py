from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, GenericAPIView, DestroyAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from gse.permissions.permissions import IsAdminOrOwner
from gse.utils.format_errors import format_errors
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
    API for retrieving a ticket object, accessible only to owner or admin or supporter.
    """
    serializer_class = TicketSerializer
    queryset = get_all_tickets()
    permission_classes = [IsAdminOrOwner]

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response(
            data={'data': response.data},
            status=response.status_code
        )


class TicketCreateAPI(GenericAPIView):
    """
    API for creating tickets, accessible only to authenticated users.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TicketSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(
                data={'data': {'message': 'تیکت با موفقیت ثبت شد.'}},
                status=status.HTTP_201_CREATED
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )


class TicketDeleteAPI(DestroyAPIView):
    """
    API for deleting tickets, accessible only to owner or admin or supporter.
    """
    permission_classes = [IsAdminOrOwner]
    serializer_class = TicketSerializer
    queryset = get_all_tickets()
