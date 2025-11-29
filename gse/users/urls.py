from django.urls import path, include

from .apis import auth, user, profile

app_name = 'users'

password_patterns = [
    path('change/', user.ChangePasswordAPI.as_view(), name='change-password'),
    path('set/', user.SetPasswordAPI.as_view(), name='set-password'),
    path('reset/', user.ResetPasswordAPI.as_view(), name='reset-password'),
]

profile_patterns = [
    path('', profile.UserProfileAPI.as_view(), name='user-profile'),
    path('update/', profile.UserProfileUpdateAPI.as_view(), name='update-user-profile'),
    path('delete/', profile.DeleteUserAccountAPI.as_view(), name='delete-user-profile'),
]

urlpatterns = [
    path('', user.UsersListAPI.as_view(), name='users-list'),
    path('register/', auth.UserRegisterAPI.as_view(), name='user-register'),
    path("register/verify/", auth.UserVerifyAPI.as_view(), name='user-verify'),
    path('register/google/auth/redirect/', auth.GoogleLoginRedirectAPI.as_view(), name='google_login_redirect'),
    path('register/google/auth/callback/', auth.GoogleLoginApi.as_view(), name='google_login'),
    path('login/', auth.CustomTokenObtainPairView.as_view(), name='user-login'),
    path('refresh/', auth.CustomTokenRefreshAPI.as_view(), name='token-refresh'),
    path('profile/', include(profile_patterns)),
    path('password/', include(password_patterns)),
]
