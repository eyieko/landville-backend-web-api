from django.urls import path
from .views import (RegistrationAPIView,
                    EmailVerificationView, SetNewPasswordAPIView)

urlpatterns = [
    path("register/", RegistrationAPIView.as_view(), name="register"),
    path("verify/", EmailVerificationView.as_view(), name="verify"),
    path("new_password/", SetNewPasswordAPIView.as_view(),
         name="new_password"),
]
