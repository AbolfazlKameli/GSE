from django.urls import path

from . import views

app_name = 'faq'
urlpatterns = [
    path('questions/', views.QuestionListAPI.as_view(), name='questions_list'),
    path('questions/<int:pk>/', views.QuestionRetrieveAPI.as_view(), name='question_retrieve'),
    path('<int:product_id>/questions/add/', views.QuestionCreateAPI.as_view(), name='question_create'),
    path('questions/<int:pk>/delete/', views.QuestionDeleteAPI.as_view(), name='question_delete'),
]
