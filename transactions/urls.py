"""A module of urlconf for transactions app"""
from django.urls import path
from transactions.views import (
    ClientAccountAPIView,
    RetrieveUpdateDeleteAccountDetailsAPIView,
    card_pin_payment,
    card_foreign_payment,
    validate_payment,
    RetreiveTransactionsAPIView
)

app_name = 'transactions'

urlpatterns = [
    path('accounts/', ClientAccountAPIView.as_view(), name="all-accounts"),
    path('account/<account_number>',
         RetrieveUpdateDeleteAccountDetailsAPIView.as_view(),
         name="single-account"),
    path('card-pin/', card_pin_payment, name='card_pin'),
    path('card-foreign/', card_foreign_payment, name='card_foreign'),
    path('validate-card/', validate_payment, name='validate_card'),
    path('', RetreiveTransactionsAPIView.as_view(), name='transactions')
]
