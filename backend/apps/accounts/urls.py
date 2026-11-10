"""مسیرهای مربوط به ثبت‌نام، ورود و پروفایل کاربران."""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginTokenView, MeView, UserSearchView, PublicProfileView, UserPreferencesView, PasswordResetRequestView, PasswordResetConfirmView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("token/", LoginTokenView.as_view(), name="token-obtain-pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password-reset"),
    path("password-reset/confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path("me/", MeView.as_view(), name="me"),
    path("preferences/", UserPreferencesView.as_view(), name="user-preferences"),
    path("users/", UserSearchView.as_view(), name="user-search"),
    path("users/<str:username>/", PublicProfileView.as_view(), name="public-profile"),
]
