"""Module of tests for views of transactions app."""
from tests.transactions import BaseTest
from transactions.views import RetreiveTransactionsAPIView
from rest_framework.test import force_authenticate
from tests.factories.transaction_factory import TransactionFactory
from . import USER_TRANSACTIONS_URL


class TestTransactions(BaseTest):
    """Tests for the user transactions functionality"""

    def test_retreive_buyer_transactions(self):
        """test to retreive user transaction details"""
        view = RetreiveTransactionsAPIView.as_view()
        TransactionFactory.create(target_property=self.property1,
                                  buyer=self.user4)
        request = self.factory.get(USER_TRANSACTIONS_URL)
        force_authenticate(request, user=self.user4)
        response = view(request)
        self.assertEqual(response.data['message'],
                         "Transaction(s) retrieved successfully")
        self.assertEqual(response.status_code, 200)

    def test_retreive_client_transactions(self):
        """test to retreive all transaction details of a client"""
        view = RetreiveTransactionsAPIView.as_view()
        TransactionFactory.create(target_property=self.property1,
                                  buyer=self.user4)
        request = self.factory.get(USER_TRANSACTIONS_URL)
        force_authenticate(request, user=self.user1)
        response = view(request)
        self.assertEqual(response.data['message'],
                         "Transaction(s) retrieved successfully")
        self.assertEqual(response.status_code, 200)

    def test_retreive_landville_transactions(self):
        """test to retreive all transactions in Landville"""
        view = RetreiveTransactionsAPIView.as_view()
        TransactionFactory.create(target_property=self.property1,
                                  buyer=self.user4)
        request = self.factory.get(USER_TRANSACTIONS_URL)
        force_authenticate(request, user=self.user5)
        response = view(request)
        self.assertEqual(response.data['message'],
                         "Transaction(s) retrieved successfully")
        self.assertEqual(response.status_code, 200)

    def test_buyer_cant_retreive_other_buyers_transactions(self):
        """test to retreive other users transaction details"""
        view = RetreiveTransactionsAPIView.as_view()
        TransactionFactory.create(target_property=self.property1,
                                  buyer=self.user4)
        request = self.factory.get(USER_TRANSACTIONS_URL)
        force_authenticate(request, user=self.user6)
        response = view(request)
        self.assertEqual(response.data['errors'], "No transactions available")
        self.assertEqual(response.status_code, 404)

    def test_retreive_transactions_of_user_with_zero_transactions(self):
        """
        test to retreive user transaction details where user has no
        transactions yet
        """
        view = RetreiveTransactionsAPIView.as_view()
        request = self.factory.get(USER_TRANSACTIONS_URL)
        force_authenticate(request, user=self.user4)
        response = view(request)
        self.assertEqual(response.data['errors'], "No transactions available")
        self.assertEqual(response.status_code, 404)

    def test_client_admin_retreive_transactions_when_none_exists(self):
        """
        test for client admin to retreive client company transactions
        when none exists
        """
        view = RetreiveTransactionsAPIView.as_view()
        request = self.factory.get(USER_TRANSACTIONS_URL)
        force_authenticate(request, user=self.user1)
        response = view(request)
        self.assertEqual(response.data['errors'], "No transactions available")
        self.assertEqual(response.status_code, 404)

    def test_landville_admin_retreive_transactions_when_none_exists(self):
        """
        test for landville admin to retreive all landville transactions when
        none exists
        """
        view = RetreiveTransactionsAPIView.as_view()
        request = self.factory.get(USER_TRANSACTIONS_URL)
        force_authenticate(request, user=self.user5)
        response = view(request)
        self.assertEqual(response.data['errors'], "No transactions available")
        self.assertEqual(response.status_code, 404)
