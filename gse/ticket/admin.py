from django.contrib import admin

from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('owner__id', 'title', 'created_date', 'status')
    list_filter = ('status',)
