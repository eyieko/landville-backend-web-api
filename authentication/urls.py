from django.urls import path
from .views import (RegistrationAPIView, EmailVerificationView,
                    GoogleAuthAPIView, FacebookAuthAPIView, TwitterAuthAPIView, LoginAPIView)

app_name = 'authentication'

urlpatterns = [
    path("register/", RegistrationAPIView.as_view(), name="register"),
    path("verify/", EmailVerificationView.as_view(), name="verify"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path('google/', GoogleAuthAPIView.as_view(), name='google'),
    path('facebook/', FacebookAuthAPIView.as_view(), name='facebook'),
    path('twitter/', TwitterAuthAPIView.as_view(), name='twitter')

]
