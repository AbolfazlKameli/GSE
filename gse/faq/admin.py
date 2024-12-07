from django.contrib import admin

from .models import Question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('product__id', 'owner__id', 'created_date', 'status')
    list_filter = ('status',)
