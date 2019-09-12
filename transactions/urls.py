"""A module of urlconf for transactions app"""
from django.urls import path
from transactions.views import (
    ClientAccountAPIView,
    RetrieveUpdateDeleteAccountDetailsAPIView,
    card_pin_payment,
    card_foreign_payment,
    validate_payment,
    RetreiveTransactionsAPIView,
    foreign_card_validation_response,
    tokenized_card_payment,
    RetrieveDepositsApiView,
    SavedCardsListView,
    DeleteSavedCardView
)

app_name = 'transactions'

urlpatterns = [
    path('accounts/', ClientAccountAPIView.as_view(), name="all-accounts"),
    path('account/<account_number>',
         RetrieveUpdateDeleteAccountDetailsAPIView.as_view(),
         name="single-account"),
    path('card-pin/', card_pin_payment, name='card_pin'),
    path('', RetreiveTransactionsAPIView.as_view(), name='transactions'),
    path('card-foreign/',
         card_foreign_payment,
         name='card_foreign'),
    path('validate-card/', validate_payment, name='validate_card'),
    path('', RetreiveTransactionsAPIView.as_view(), name='transactions'),
    path('rave-response/', foreign_card_validation_response,
         name='validation_response'),
    path(
         'tokenized-card/<int:saved_card_id>',
         tokenized_card_payment, name='tokenized_card'),
    path('my-deposit/', RetrieveDepositsApiView.as_view(), name='my_deposit'),
        path('saved-cards/',
         SavedCardsListView.as_view(), name='saved-cards'),
    path(
         'saved-card/<int:id>',
         DeleteSavedCardView.as_view(), name='saved-card'),
]
