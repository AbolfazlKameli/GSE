from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from gse.website.exceptions import custom_page_not_found

documents = [
    path('', SpectacularAPIView.as_view(), name='schema'),
    path('swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('gse.users.urls', namespace='users')),
    path('products/', include('gse.products.urls', namespace='products')),
    path('cart/', include('gse.cart.urls', namespace='cart')),
    path('orders/', include('gse.orders.urls', namespace='orders')),
    path('website/', include('gse.website.urls', namespace='website')),
    path('payment/', include('gse.payment.urls', namespace='payment')),
    path('faq/', include('gse.faq.urls', namespace='faq')),
    path('schema/', include(documents))
]

if settings.DEBUG and 'debug_toolbar' in settings.INSTALLED_APPS:
    urlpatterns = [
                      path('__debug__/', include('debug_toolbar.urls'))
                  ] + urlpatterns

handler404 = custom_page_not_found
