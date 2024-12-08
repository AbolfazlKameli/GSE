from django.db import transaction

from .models import Ticket, TicketAnswer
from .choices import TICKET_STATUS_ANSWERED


@transaction.atomic
def submit_answer(ticket: Ticket, title: str, body: str):
    answer = TicketAnswer.objects.create(
        title=title,
        body=body,
        ticket=ticket
    )
    ticket.status = TICKET_STATUS_ANSWERED
    ticket.save()
    return answer
