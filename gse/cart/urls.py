from django.urls import path

from . import views

app_name = 'cart'

urlpatterns = [
    path('<int:pk>/', views.CartRetrieveAPI.as_view(), name='cart_retrieve'),
    path('add/', views.CartItemAddAPI.as_view(), name='cart_create'),
    path('<int:pk>/update/', views.CartItemUpdateAPI.as_view(), name='cart_update'),
    path('<int:pk>/delete/', views.CartItemDeleteAPI.as_view(), name='cart_delete')
]
