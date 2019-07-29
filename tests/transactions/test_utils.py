from datetime import datetime
from tests.transactions.test_models import TransactionTest, SavingsTest
from transactions.transaction_utils import (save_deposit,)
from ..factories.transaction_factory import TransactionFactory, SavingsFactory

references = {
    'txRef': '{}_LAND{}'.format('TAX', datetime.now()),
    'orderRef': '{}_LAND{}'.format('ORDER', datetime.now()),
    'flwRef': '{}_LAND{}'.format('FLW', datetime.now()),
    'raveRef': '{}_LAND{}'.format('RAV', datetime.now()),
}


class TestDepositSavingUtils(SavingsTest):
    amount = 1000

    def test_should_update_savings(self):
        """
        test if the deposit for a saving is saved and and the saving amount is
        updated
        """
        old_saving = SavingsFactory(owner=self.user1)
        deposit, new_savings = save_deposit('Saving', references,
                                            self.amount, self.user1,
                                            'test test')
        self.assertIsNotNone(deposit)
        self.assertEqual(float(old_saving.balance+self.amount),
                         float(new_savings.balance))
        self.assertNotEqual(new_savings.balance, self.amount)

    def test_should_not_update_savings_when_creating_anew(self):
        """
        test if a saving amount is not updated when creating a new saving
        """
        deposit, new_savings = save_deposit('Saving', references,
                                            self.amount, self.user1,
                                            'test test')
        self.assertIsNotNone(deposit)
        self.assertEqual(new_savings.balance, self.amount)


class TestDepositTransactionUtils(TransactionTest):
    amount = 1000

    def test_should_insert_transaction(self):
        """
        test if the deposit for a transaction is saved and
        the amount payed is updated
        """
        old_transaction = TransactionFactory(amount_paid=self.amount,
                                             target_property=self.property1,
                                             buyer=self.buyer1)
        deposit, new_transaction = save_deposit('Buying',
                                                references,
                                                self.amount,
                                                self.buyer1,
                                                self.property1,
                                                'test test')
        self.assertIsNotNone(deposit)
        self.assertEqual(float(old_transaction.amount_paid + self.amount),
                         float(new_transaction.amount_paid))
        self.assertNotEqual(new_transaction.amount_paid, self.amount)

    def test_should_not_update_transaction_when_creating_anew(self):
        """
        test if a transaction amount is not updated when creating a new saving
        """
        deposit, new_transaction = save_deposit('Buying', references,
                                                self.amount, self.buyer1,
                                                self.property1, 'test test')
        self.assertIsNotNone(deposit)
        self.assertEqual(new_transaction.amount_paid, self.amount)
