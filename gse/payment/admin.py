from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('ref_id', 'status', 'id', 'response_code')
    list_filter = ('status',)
