from django.urls import path

from . import views

app_name = 'ticket'
urlpatterns = [
    path('', views.TicketsListAPI.as_view(), name='tickets_list')
]
