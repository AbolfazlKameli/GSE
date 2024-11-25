from django.urls import path

from . import views

app_name = 'orders'
urlpatterns = [
    path('', views.UserOrdersListAPI.as_view(), name='orders_list'),
    path('<int:pk>/', views.OrderRetrieveAPI.as_view(), name='order_retrieve'),
    path('add/', views.OrderCreateAPI.as_view(), name='order_create'),
    path('<int:order_id>/items/<int:pk>/delete/', views.OrderItemDeleteAPI.as_view(), name='delete_order_item'),
    path('<int:pk>/cancel/', views.OrderCancelAPI.as_view(), name='cancel_order'),
    path('coupons/<int:pk>/', views.CouponRetrieveAPI.as_view(), name='coupon_retrieve'),
]
