from django.http import Http404
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, GenericAPIView, DestroyAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from gse.permissions.permissions import IsAdminOrOwner, IsAdminOrSupporter
from gse.utils.db_utils import is_child_of
from gse.utils.format_errors import format_errors
from .models import Ticket, TicketAnswer
from .selectors import get_all_tickets, get_answer_by_id, get_ticket_by_id
from .serializers import TicketsListSerializer, TicketSerializer, TicketAnswerSerializer


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


class TicketAnswerRetrieveAPI(GenericAPIView):
    """
    API for retrieving ticket answers, accessible to ticket owner or admin or supporter.
    """
    serializer_class = TicketAnswerSerializer
    permission_classes = [IsAdminOrOwner]

    def get_object(self):
        if not is_child_of(Ticket, TicketAnswer, self.kwargs.get('ticket_id'), self.kwargs.get('answer_id')):
            raise Http404('پاسخ مرتبط با تیکت با این مشخصات پیدا نشد.')
        answer: TicketAnswer = get_answer_by_id(answer_id=self.kwargs.get('answer_id'))
        if answer:
            self.check_object_permissions(self.request, answer.ticket)
            return answer
        raise Http404('پاسخ مورد نظر پیدا نشد.')

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(instance=self.get_object())
        return Response(
            data={'data': serializer.data},
            status=status.HTTP_200_OK
        )


class TicketAnswerCreateAPI(GenericAPIView):
    """
    API for creating ticket answers, accessible only to admin or supporter.
    """
    serializer_class = TicketAnswerSerializer
    permission_classes = [IsAdminOrSupporter]

    def get_object(self):
        ticket: Ticket = get_ticket_by_id(ticket_id=self.kwargs.get('ticket_id'))
        if ticket:
            return ticket
        raise Http404('تیکت درحال پردازشی با این مشخصات پیدا نشد.')

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            ticket = self.get_object()
            serializer.save(ticket=ticket)
            return Response(
                data={'data': {'message': 'پاسخ تیکت با موفقیت ثبت شد.'}},
                status=status.HTTP_201_CREATED
            )
        return Response(
            data={'data': {'errors': format_errors(serializer.errors)}},
            status=status.HTTP_400_BAD_REQUEST
        )
