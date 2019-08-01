"""Module of tests for views of transactions app."""
import json
from tests.transactions import BaseTest
from django.urls import reverse
from rest_framework.test import force_authenticate
from rest_framework.views import status
from transactions.serializers import DepositSerializer
from transactions.models import Deposit
from transactions.views import RetrieveDepositsApiView
from tests.factories.transaction_factory import SavingsFactory
from transactions.transaction_utils import save_deposit
from ..test_utils import references
from django.db.models import Q


class TestReturnAllMyDeposit(BaseTest):
    def test_should_return_all_my_deposit(self):
        """
        This test ensure that I can get all my deposit
        """
        amount_to_save = 100
        savings = SavingsFactory.create(owner=self.user4)
        deposit, saving_updated = save_deposit('Saving', references,
                                               amount_to_save, self.user4,
                                               'test test')
        request = self.factory.get(reverse("transactions:my_deposit"),
                                   format='json')
        force_authenticate(request, user=self.user4)
        view = RetrieveDepositsApiView.as_view()
        response = view(request, format='json')
        expected = Deposit.objects.select_related(
            'transaction', 'account').filter(
                Q(transaction__buyer__id=self.user4.id)
                | Q(account__owner__id=self.user4.id))
        serialized = DepositSerializer(expected, many=True)
        results = response.data.get('results')
        self.assertEqual(results, serialized.data)
        self.assertTrue(results[0].get('saving_account'))
        self.assertEqual(
            float(results[0].get('saving_account').get('balance')),
            float(saving_updated.balance))
        self.assertEqual(float(results[0].get('amount')),
                         float(deposit.amount))
        self.assertEqual(savings.owner.id, self.user4.id)
        self.assertIsInstance(results[0].get('references'), dict)
        self.assertEqual(results[0].get('references'),
                         json.loads(deposit.references))
        self.assertIsNotNone(results[0].get('created_at'))
        self.assertEqual(savings.balance + amount_to_save,
                         float(saving_updated.balance))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_if_the_landville_admin_has_has_access_to_all_deposits(self):
        request = self.factory.get(reverse("transactions:my_deposit"),
                                   format='json')
        force_authenticate(request, user=self.user_land_admin)
        view = RetrieveDepositsApiView.as_view()
        response = view(request, format='json')
        expected = Deposit.objects.select_related('transaction',
                                                  'account').all()
        serialized = DepositSerializer(expected, many=True)
        results = response.data.get('results')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(results, serialized.data)

    def test_if_an_unauthenticated_user_get_403_when_no_deposit(self):
        request = self.factory.get(reverse("transactions:my_deposit"),
                                   format='json')
        view = RetrieveDepositsApiView.as_view()
        response = view(request, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_client_admin_should_receive_all_deposit_for_his_company(self):
        transaction = self.create_transaction(user_role=self.user1.role)
        save_deposit('Buying', references, 1000,
                     self.user4,
                     transaction.target_property,
                     'test test')
        request = self.factory.get(reverse("transactions:my_deposit"),
                                   format='json')
        force_authenticate(request, user=self.user1)
        view = RetrieveDepositsApiView.as_view()
        response = view(request, format='json')
        expected = Deposit.objects.select_related(
            'transaction', 'transaction__target_property')
        expected = expected.filter(
            transaction__target_property__client_id=self.user1.employer.first(
            ).id)
        serialized = DepositSerializer(expected, many=True)
        results = response.data.get('results')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(results, serialized.data)
