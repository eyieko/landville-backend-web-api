from django.urls import path
from authentication.views import (
    RegistrationAPIView, EmailVerificationView,
    ClientCreateView,
    GoogleAuthAPIView,
    FacebookAuthAPIView,
    TwitterAuthAPIView,
    LoginAPIView,
    PasswordResetView,
    ProfileView,
    AddReasonView)

app_name = 'authentication'

urlpatterns = [
    path("register/", RegistrationAPIView.as_view(), name="register"),
    path("verify/", EmailVerificationView.as_view(), name="verify"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path('google/', GoogleAuthAPIView.as_view(), name='google'),
    path('facebook/', FacebookAuthAPIView.as_view(), name='facebook'),
    path('twitter/', TwitterAuthAPIView.as_view(), name='twitter'),
    path("client/", ClientCreateView.as_view(), name="client"),
    path("password-reset/", PasswordResetView.as_view(), name="password-reset"),
    path("admin/notes/", AddReasonView.as_view(), name='add-notes'),
    path("profile/", ProfileView.as_view(), name="profile"),
]
