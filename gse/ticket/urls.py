from django.urls import path

from . import views

app_name = 'ticket'
urlpatterns = [
    # Tickets
    path('', views.TicketsListAPI.as_view(), name='tickets_list'),
    path('<int:ticket_id>/', views.TicketRetrieveAPI.as_view(), name='ticket_retrieve'),
    path('add/', views.TicketCreateAPI.as_view(), name='ticket_create'),
    path('<int:ticket_id>/delete/', views.TicketDeleteAPI.as_view(), name='ticket_delete'),

    # Answer
    path(
        '<int:ticket_id>/answers/<int:answer_id>/',
        views.TicketAnswerRetrieveAPI.as_view(),
        name='ticket_answer_retrieve'
    ),
    path('<int:ticket_id>/answers/add/', views.TicketAnswerCreateAPI.as_view(), name='ticket_answer_create'),
    path(
        '<int:ticket_id>/answers/<int:answer_id>/delete/',
        views.TicketAnswerDeleteAPI.as_view(),
        name='ticket_answer_delete'
    ),
]
