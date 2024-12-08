from .models import Ticket


def get_all_tickets() -> list[Ticket]:
    return Ticket.objects.all()
