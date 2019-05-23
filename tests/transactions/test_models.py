from django.test import TestCase

from ..factories.authentication_factory import UserFactory, ClientFactory
from ..factories.transaction_factory import (
    TransactionFactory, SavingsFactory, DepositFactory, ClientAccountFactory
)
from ..factories.property_factory import PropertyFactory


class TransactionTest(TestCase):
    """This class defines tests for the transaction model"""

    def setUp(self):
        self.user1 = UserFactory.create()
        self.client1 = ClientFactory.create(client_admin=self.user1)
        self.property1 = PropertyFactory.create(client=self.client1)
        self.buyer1 = UserFactory.create()

    def test_that_the_string_representation_works(self):
        transaction = TransactionFactory.create(
            target_property=self.property1, buyer=self.buyer1)
        self.assertEqual(
            str(transaction), f'{transaction.status} transaction for {self.property1}')


class DepositTest(TestCase):
    """This class defines tests for the deposit model"""

    def setUp(self):
        self.user1 = UserFactory.create()
        self.savings1 = SavingsFactory.create(owner=self.user1)

    def test_that_the_string_representation_works(self):
        deposit = DepositFactory.create(account=self.savings1)
        self.assertEqual(
            str(deposit), f'{deposit.amount} amount deposit for {deposit.account}')


class SavingsTest(TestCase):
    """This class defines tests for the savings model"""

    def setUp(self):
        self.user1 = UserFactory.create()

    def test_that_the_string_representation_works(self):
        savings = SavingsFactory.create(owner=self.user1)
        self.assertEqual(
            str(savings), f'Savings by {savings.owner}')


class ClientAccountTest(TestCase):
    """This class defines tests for the client accounts model"""

    def setUp(self):
        self.user1 = UserFactory.create()
        self.client1 = ClientFactory.create(client_admin=self.user1)

    def test_that_the_string_representation_works(self):
        account = ClientAccountFactory.create(owner=self.client1)
        self.assertEqual(
            str(account), f"{account.owner}'s account for {account.bank_name}")
