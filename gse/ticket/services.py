from django.db import transaction

from .choices import TICKET_STATUS_ANSWERED, TICKET_STATUS_PENDING
from .models import Ticket, TicketAnswer


@transaction.atomic
def submit_answer(ticket: Ticket, title: str, body: str) -> TicketAnswer:
    answer = TicketAnswer.objects.create(
        title=title,
        body=body,
        ticket=ticket
    )
    ticket.status = TICKET_STATUS_ANSWERED
    ticket.save()
    return answer


@transaction.atomic
def remove_answer(ticket: Ticket, answer: TicketAnswer) -> Ticket:
    answer.delete()
    ticket.status = TICKET_STATUS_PENDING
    ticket.save()
    return ticket
