from django.urls import path, include
from transactions.views import ClientAccountAPIView, RetrieveUpdateDeleteAccountDetailsAPIView

app_name = 'transactions'

urlpatterns = [
    path('accounts/', ClientAccountAPIView.as_view(), name="all-accounts"),
    path('account/<account_number>',
         RetrieveUpdateDeleteAccountDetailsAPIView.as_view(), name="single-account"),
]
