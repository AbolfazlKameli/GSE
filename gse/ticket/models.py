from django.db import models

from gse.users.models import User
from .choices import TICKET_STATUS_CHOICES, TICKET_STATUS_PENDING


class Ticket(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    title = models.CharField(max_length=255)
    body = models.TextField()
    status = models.CharField(choices=TICKET_STATUS_CHOICES, default=TICKET_STATUS_PENDING, max_length=10)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_date',)


class TicketAnswer(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name='answer')
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_date',)
