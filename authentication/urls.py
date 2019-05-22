from django.urls import path, include
from .views import GoogleAuthAPIView, FacebookAuthAPIView, TwitterAuthAPIView

app_name = 'authentication'

urlpatterns = [
    path('google/', GoogleAuthAPIView.as_view(), name='google'),
    path('facebook/', FacebookAuthAPIView.as_view(), name='facebook'),
    path('twitter/', TwitterAuthAPIView.as_view(), name='twitter')
]
