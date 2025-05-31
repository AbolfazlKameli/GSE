from django.urls import path, include

from .apis import categories, products, details, media, reviews

app_name = 'products'

category_patterns = [
    path('', categories.CategoriesListAPI.as_view(), name='categories_list'),
    path('<int:category_id>/', categories.CategoryRetrieveAPI.as_view(), name='category_retrieve'),
    path('<int:category_id>/update/', categories.CategoryUpdateAPI.as_view(), name='category_update'),
    path('<int:category_id>/delete/', categories.CategoryDeleteAPI.as_view(), name='category_delete'),
    path('add/', categories.CategoryCreateAPI.as_view(), name='category_create'),
]

product_patterns = [
    path('', products.ProductsListAPI.as_view(), name='products_list'),
    path('<int:product_id>/', products.ProductRetrieveAPI.as_view(), name='product_retrieve'),
    path('<int:product_id>/update/', products.ProductUpdateAPI.as_view(), name='product_update'),
    path('<int:product_id>/delete/', products.ProductDestroyAPI.as_view(), name='product_delete'),
    path('add/', products.ProductCreateAPI.as_view(), name='product_create'),
]

detail_patterns = [
    path('<int:detail_id>/update/', details.ProductDetailUpdateAPI.as_view(), name='detail_update'),
    path('<int:detail_id>/delete/', details.ProductDetailDeleteAPI.as_view(), name='detail_delete'),
    path('add/', details.ProductDetailCreateAPI.as_view(), name='detail_create'),
]

media_patterns = [
    path('add/', media.ProductMediaCreateAPI.as_view(), name='media_create'),
    path('<int:media_id>/update/', media.ProductMediaUpdateAPI.as_view(), name='media_update'),
    path('<int:media_id>/delete/', media.ProductMediaDeleteAPI.as_view(), name='media_delete'),
]

review_patterns = [
    path('', reviews.ProductReviewListAPI.as_view(), name='product_review_list'),
    path(
        '<int:review_id>/',
        reviews.ProductReviewRetrieve.as_view(),
        name='product_review_retrieve'
    ),
    path('add/', reviews.ProductReviewCreateAPI.as_view(), name='product_review_create'),
    path(
        '<int:review_id>/delete/',
        reviews.ProductReviewDeleteAPI.as_view(),
        name='product_review_delete'
    ),
]

urlpatterns = [
    path('categories/', include(category_patterns)),
    path('', include(product_patterns)),
    path('<int:product_id>/details/', include(detail_patterns)),
    path('<int:product_id>/media/', include(media_patterns)),
    path('<int:product_id>/reviews/', include(review_patterns))
]
