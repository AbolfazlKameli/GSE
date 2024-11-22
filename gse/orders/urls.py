from django.urls import path

from . import views

app_name = 'orders'
urlpatterns = [
    path('<int:pk>/', views.OrderRetrieveAPI.as_view(), name='order_retrieve'),
    path('add/', views.OrderCreateAPI.as_view(), name='order_create'),
    path('items/<int:pk>/delete/', views.OrderItemDeleteAPI.as_view(), name='delete_order_item')
]
