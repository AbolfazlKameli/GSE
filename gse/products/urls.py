from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductsListAPI.as_view(), name='products_list'),
    path('<int:pk>/', views.ProductRetrieveAPI.as_view(), name='product_retrieve'),
    path('<int:pk>/delete/', views.ProductDestroyAPI.as_view(), name='product_delete'),
    path('add/', views.ProductCreateAPI.as_view(), name='product_create')
]
