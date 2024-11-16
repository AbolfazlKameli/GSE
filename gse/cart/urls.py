from django.urls import path

from . import views

app_name = 'cart'

urlpatterns = [
    path('<int:pk>/', views.CartRetrieveAPI.as_view(), name='cart_retrieve')
]
