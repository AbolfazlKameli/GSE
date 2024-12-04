from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [
    # Categories
    path('categories/', views.CategoriesListAPI.as_view(), name='categories_list'),
    path('categories/<int:pk>/', views.CategoryRetrieveAPI.as_view(), name='category_retrieve'),
    path('categories/<int:pk>/update/', views.CategoryUpdateAPI.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteAPI.as_view(), name='category_delete'),
    path('categories/add/', views.CategoryCreateAPI.as_view(), name='category_create'),

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
    path('<int:pk>/media/<int:media_id>/delete/', views.ProductMediaDeleteAPI.as_view(), name='media_delete'),

    # Reviews
    path('<int:pk>/reviews/', views.ProductReviewListAPI.as_view(), name='product_review_list'),
    path('<int:pk>/reviews/<int:review_id>/', views.ProductReviewRetrieve.as_view(), name='product_review_retrieve'),
    path(
        '<int:pk>/reviews/<int:review_id>/delete/',
        views.ProductReviewDeleteAPI.as_view(),
        name='product_review_delete'
    ),
]
