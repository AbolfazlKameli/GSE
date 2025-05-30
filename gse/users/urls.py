from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

app_name = 'users'

token = [
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('block-token/', views.BlockTokenAPI.as_view(), name='token-block'),
]

password = [
    path('change/', views.ChangePasswordAPI.as_view(), name='change-password'),
    path('set/', views.SetPasswordAPI.as_view(), name='set-password'),
    path('reset/', views.ResetPasswordAPI.as_view(), name='reset-password'),
]

profile = [
    path('', views.UserProfileAPI.as_view(), name='user-profile'),
    path('update/', views.UserProfileUpdateAPI.as_view(), name='update-user-profile'),
    path('delete/', views.DeleteUserAccountAPI.as_view(), name='delete-user-profile'),
]

urlpatterns = [
    path('', views.UsersListAPI.as_view(), name='users-list'),
    path('register/', views.UserRegisterAPI.as_view(), name='user-register'),
    path('register/verify/', views.UserVerificationAPI.as_view(), name='user-register-verify'),
    path('register/google/auth/redirect/', views.GoogleLoginRedirectAPI.as_view(), name='google_login_redirect'),
    path('register/google/auth/callback/', views.GoogleLoginApi.as_view(), name='google_login'),
    path('resend-email/', views.ResendVerificationEmailAPI.as_view(), name='user-register-resend-email'),
    path('login/', views.CustomTokenObtainPairView.as_view(), name='user-login'),
    path('profile/', include(profile)),
    path('token/', include(token)),
    path('password/', include(password)),
]
