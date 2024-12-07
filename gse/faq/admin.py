from django.contrib import admin

from .models import Question, Answer


class AnswerInline(admin.TabularInline):
    model = Answer
    fields = ('body',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('product__id', 'owner__id', 'created_date', 'status')
    list_filter = ('status',)
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question__id', 'created_date', 'body')
