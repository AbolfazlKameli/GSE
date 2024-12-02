from django.urls import path

from . import views

app_name = 'payment'
urlpatterns = [
    path('pay/<int:order_id>/', views.ZPPaymentAPI.as_view(), name='ZP_pay'),
    path('pay/verify/', views.ZPVerifyAPI.as_view(), name='ZP_verify'),
    path('<int:payment_id>/receipt/', views.PaymentReceiptAPI.as_view(), name='receipt'),
]
