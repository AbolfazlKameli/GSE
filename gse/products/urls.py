from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [
    # Categories
    path('categories/', views.CategoriesListAPI.as_view(), name='categories_list'),
    path('categories/<int:category_id>/', views.CategoryRetrieveAPI.as_view(), name='category_retrieve'),
    path('categories/<int:category_id>/update/', views.CategoryUpdateAPI.as_view(), name='category_update'),
    path('categories/<int:category_id>/delete/', views.CategoryDeleteAPI.as_view(), name='category_delete'),
    path('categories/add/', views.CategoryCreateAPI.as_view(), name='category_create'),

    # Products
    path('', views.ProductsListAPI.as_view(), name='products_list'),
    path('<int:product_id>/', views.ProductRetrieveAPI.as_view(), name='product_retrieve'),
    path('<int:product_id>/update/', views.ProductUpdateAPI.as_view(), name='product_update'),
    path('<int:product_id>/delete/', views.ProductDestroyAPI.as_view(), name='product_delete'),
    path('add/', views.ProductCreateAPI.as_view(), name='product_create'),

    # Details
    path(
        '<int:product_id>/details/<int:detail_id>/update/',
        views.ProductDetailUpdateAPI.as_view(),
        name='detail_update'
    ),
    path(
        '<int:product_id>/details/<int:detail_id>/delete/',
        views.ProductDetailDeleteAPI.as_view(),
        name='detail_delete'
    ),
    path('<int:product_id>/details/add/', views.ProductDetailCreateAPI.as_view(), name='detail_create'),

    # Media
    path('<int:product_id>/media/add/', views.ProductMediaCreateAPI.as_view(), name='media_create'),
    path('<int:product_id>/media/<int:media_id>/update/', views.ProductMediaUpdateAPI.as_view(), name='media_update'),
    path('<int:product_id>/media/<int:media_id>/delete/', views.ProductMediaDeleteAPI.as_view(), name='media_delete'),

    # Reviews
    path('<int:product_id>/reviews/', views.ProductReviewListAPI.as_view(), name='product_review_list'),
    path(
        '<int:product_id>/reviews/<int:review_id>/',
        views.ProductReviewRetrieve.as_view(),
        name='product_review_retrieve'
    ),
    path('<int:product_id>/review/add/', views.ProductReviewCreateAPI.as_view(), name='product_review_create'),
    path(
        '<int:product_id>/reviews/<int:review_id>/delete/',
        views.ProductReviewDeleteAPI.as_view(),
        name='product_review_delete'
    ),
]
