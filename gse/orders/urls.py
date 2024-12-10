from django.urls import path

from . import views

app_name = 'orders'
urlpatterns = [
    path('', views.UserOrdersListAPI.as_view(), name='orders_list'),
    path('<int:order_id>/', views.OrderRetrieveAPI.as_view(), name='order_retrieve'),
    path('add/', views.OrderCreateAPI.as_view(), name='order_create'),
    path('<int:order_id>/items/<int:item_id>/delete/', views.OrderItemDeleteAPI.as_view(), name='delete_order_item'),
    path('<int:order_id>/cancel/', views.OrderCancelAPI.as_view(), name='cancel_order'),
    path('coupons/<int:coupon_id>/', views.CouponRetrieveAPI.as_view(), name='coupon_retrieve'),
    path('coupon/add/', views.CouponCreateAPI.as_view(), name='coupon_create'),
    path('coupon/<int:coupon_id>/update/', views.CouponUpdateAPI.as_view(), name='coupon_update'),
    path('coupon/<int:coupon_id>/delete/', views.CouponDeleteAPI.as_view(), name='coupon_delete'),
    path('coupon/apply/', views.CouponApplyAPI.as_view(), name='coupon_apply'),
    path('coupon/discard/', views.CouponDiscardAPI.as_view(), name='coupon_discard'),
]
