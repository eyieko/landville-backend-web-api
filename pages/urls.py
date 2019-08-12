from django.urls import path
from .views import TermsView

urlpatterns = [
    path('', TermsView.as_view(), name="terms")
]
