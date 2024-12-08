from django.urls import path

from . import views

app_name = 'ticket'
urlpatterns = [
    # Tickets
    path('', views.TicketsListAPI.as_view(), name='tickets_list'),
    path('<int:pk>/', views.TicketRetrieveAPI.as_view(), name='ticket_retrieve'),
    path('add/', views.TicketCreateAPI.as_view(), name='ticket_create'),
    path('<int:pk>/delete/', views.TicketDeleteAPI.as_view(), name='ticket_delete'),

    # Answer
    path(
        '<int:ticket_id>/answers/<int:answer_id>/',
        views.TicketAnswerRetrieveAPI.as_view(),
        name='ticket_answer_retrieve'
    ),
]
