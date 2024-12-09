from django.urls import path

from . import views

app_name = 'website'
urlpatterns = [
    path('attributes/add/', views.WebsiteAttributeCreateAPI.as_view(), name='website_attr_create'),
    path('attributes/<int:attr_id>/update/', views.WebsiteAttributeUpdateAPI.as_view(), name='website_attr_update'),
    path('attributes/', views.WebSiteAttributeListAPI.as_view(), name='website_attr_list'),
]
