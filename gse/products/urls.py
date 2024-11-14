from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [
    # Products
    path('', views.ProductsListAPI.as_view(), name='products_list'),
    path('<int:pk>/', views.ProductRetrieveAPI.as_view(), name='product_retrieve'),
    path('<int:pk>/update/', views.ProductUpdateAPI.as_view(), name='product_update'),
    path('<int:pk>/delete/', views.ProductDestroyAPI.as_view(), name='product_delete'),
    path('add/', views.ProductCreateAPI.as_view(), name='product_create'),

    # Details
    path('<int:pk>/details/<int:detail_id>/update/', views.ProductDetailUpdateAPI.as_view(), name='detail_update'),
    path('<int:pk>/details/<int:detail_id>/delete/', views.ProductDetailDeleteAPI.as_view(), name='detail_delete'),
    path('<int:pk>/details/add/', views.ProductDetailCreateAPI.as_view(), name='detail_create'),

    # Media
    path('<int:pk>/media/add/', views.ProductMediaCreateAPI.as_view(), name='media_create'),
    path('<int:pk>/media/<int:media_id>/update/', views.ProductMediaUpdateAPI.as_view(), name='media_update'),
]
