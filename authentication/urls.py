from django.urls import path
from .views import RegistrationAPIView, EmailVerificationView

urlpatterns = [
    path("register/", RegistrationAPIView.as_view(), name="register"),
    path("verify/", EmailVerificationView.as_view(), name="verify"),
]
