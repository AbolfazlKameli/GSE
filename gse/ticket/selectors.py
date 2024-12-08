from .choices import TICKET_STATUS_PENDING
from .models import Ticket, TicketAnswer


def get_all_tickets() -> list[Ticket]:
    return Ticket.objects.select_related('answers').all()


def get_ticket_by_id(ticket_id: int, status: str = TICKET_STATUS_PENDING) -> Ticket | None:
    return Ticket.objects.filter(id=ticket_id, status=status).first()


def get_answer_by_id(answer_id: int) -> TicketAnswer | None:
    return TicketAnswer.objects.filter(id=answer_id).first()


def get_all_ticket_answers() -> list[TicketAnswer]:
    return TicketAnswer.objects.all()
