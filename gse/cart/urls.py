from django.urls import path

from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.CartRetrieveAPI.as_view(), name='cart_retrieve'),
    path('items/add/', views.CartItemAddAPI.as_view(), name='cart_create'),
    path('items/<int:item_id>/delete/', views.CartItemDeleteAPI.as_view(), name='cart_delete')
]
