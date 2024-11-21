from django.urls import path

from . import views

app_name = 'orders'
urlpatterns = [
    path('<int:pk>/', views.OrderRetrieveAPI.as_view(), name='order_retrieve')
]
