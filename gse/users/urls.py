from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

app_name = 'users'

token = [
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('block-token/', views.BlockTokenAPI.as_view(), name='token-block'),
]

password = [
    path('change/', views.ChangePasswordAPI.as_view(), name='change-password'),
    path('set/<str:token>/', views.SetPasswordAPI.as_view(), name='set-password'),
    path('reset/', views.ResetPasswordAPI.as_view(), name='reset-password'),
]

profile = [
    path('<int:id>/', views.UserProfileAPI.as_view(), name='user-profile'),
    path('<int:id>/update/', views.UserProfileUpdateAPI.as_view(), name='update-user-profile'),
    path('<int:id>/delete/', views.DeleteUserAccountAPI.as_view(), name='update-user-profile'),
]

urlpatterns = [
    path('', views.UsersListAPI.as_view(), name='users-list'),
    path('register/', views.UserRegisterAPI.as_view(), name='user-register'),
    path('register/verify/<str:token>/', views.UserRegisterVerifyAPI.as_view(), name='user-register-verify'),
    path('resend-email/', views.ResendVerificationEmailAPI.as_view(), name='user-register-resend-email'),
    path('profile/', include(profile)),
    path('token/', include(token)),
    path('password/', include(password))
]
