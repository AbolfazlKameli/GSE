from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner__email', 'status')
    list_filter = ('status',)
    search_fields = ('owner__email',)
