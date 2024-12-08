from django.contrib import admin

from .models import Ticket, TicketAnswer


class TicketAnswerInline(admin.TabularInline):
    model = TicketAnswer
    fields = ('title', 'body')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('owner__id', 'title', 'created_date', 'status')
    list_filter = ('status',)
    inlines = [TicketAnswerInline]


@admin.register(TicketAnswer)
class TicketAnswerAdmin(admin.ModelAdmin):
    list_display = ('ticket__id', 'title', 'created_date')
