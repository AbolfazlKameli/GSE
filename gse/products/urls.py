from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [
    path('list/', views.ProductsListAPI.as_view(), name='products_list'),
    path('<int:pk>/', views.ProductRetrieveAPI.as_view(), name='products_retrieve'),
    path('', views.ProductCreateAPI.as_view(), name='product_create')
]
