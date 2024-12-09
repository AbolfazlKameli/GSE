from django.urls import path

from . import views

app_name = 'website'
urlpatterns = [
    path('attributes/add/', views.WebsiteAttributeCreateAPI.as_view(), name='website_attr_create'),
]
