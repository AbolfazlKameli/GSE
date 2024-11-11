from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductsListAPI.as_view(), name='products_list'),
    path('<int:pk>/', views.ProductRetrieveAPI.as_view(), name='products_retrieve')
]
