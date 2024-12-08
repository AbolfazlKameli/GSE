from .models import Ticket, TicketAnswer


def get_all_tickets() -> list[Ticket]:
    return Ticket.objects.select_related('answers').all()


def get_answer_by_id(answer_id: int) -> TicketAnswer | None:
    return TicketAnswer.objects.filter(id=answer_id).first()
