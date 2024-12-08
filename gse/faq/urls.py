from django.urls import path

from . import views

app_name = 'faq'
urlpatterns = [
    # Questions
    path('questions/', views.QuestionListAPI.as_view(), name='questions_list'),
    path(
        'questions/product/<int:product_id>/list/',
        views.ProductQuestionListAPI.as_view(),
        name='product_questions_list'
    ),
    path('questions/<int:pk>/', views.QuestionRetrieveAPI.as_view(), name='question_retrieve'),
    path('<int:product_id>/questions/add/', views.QuestionCreateAPI.as_view(), name='question_create'),
    path('questions/<int:pk>/delete/', views.QuestionDeleteAPI.as_view(), name='question_delete'),

    # Answers
    path('questions/<int:question_id>/answers/add/', views.AnswerCreateAPI.as_view(), name='answer_create'),
    path(
        'questions/<int:question_id>/answers/<int:answer_id>/delete/',
        views.AnswerDeleteAPI.as_view(),
        name='answer_delete'
    ),
]
