"""Module of tests for TransactionServices helper class."""
from django.test import TestCase
from faker import Factory
from mock import patch
from transactions.transaction_services import TransactionServices
from tests.factories.authentication_factory import UserFactory, CardInfoFactory
from authentication.models import User, CardInfo


class TestTransactionServices(TestCase):
    """
    This class holds the unit tests for methods defined in the
    TransactionServices helper class
    """

    def setUp(self):
        self.faker = Factory.create()
        self.test_data = {
            'cardno': self.faker.credit_card_number(card_type=None),
            'cvv': self.faker.credit_card_security_code(card_type=None),
            'expirymonth': self.faker.credit_card_expire(
                start='now', end='+10y', date_format='%m'),
            'expiryyear': self.faker.credit_card_expire(
                start='now', end='+10y', date_format='%y'),
            'amount': 20000.00,
            'pin': 1111
        }
        self.payload = {'data': {
            'tx': {'txRef': 'sampletxref'}, 'meta': [{'metavalue': 1}],
            'vbvmessage': 'somemessage', 'status': 'successful',
            'custemail': 'email@email.com', 'card': {
                'expirymonth': '11', 'expiryyear': 22, 'last4digits': 1234,
                'card_tokens': [{'embedtoken': 'sometoken'}],
                'brand': 'somebrand'}}
        }

    @patch('transactions.transaction_services.requests.post')
    def test_initiate_payment(self, mock_post):
        """A unit test for the method for initiating card payment"""

        mock_post.return_value.json.return_value = {
            "status": "success",
            "message": "AUTH_SUGGESTION",
            "data": {
                "suggested_auth": "PIN"
            }
        }

        resp = TransactionServices.initiate_card_payment(self.test_data)
        self.assertEqual(resp['status'], 'success')

    @patch('transactions.transaction_services.requests.post')
    def test_authenticate_payment(self, mock_post):
        """A unit test for the method for authenticating card payment"""
        mock_post.return_value.json.return_value = {
            'status': 'success',
            'message': 'V-COMP'
        }
        self.test_data.update({'auth_dict': {
            'suggested_auth': 'PIN', 'pin': 3310
        }})
        resp = TransactionServices.authenticate_card_payment(self.test_data)
        self.assertEqual(resp['status'], 'success')

    @patch('transactions.transaction_services.requests.post')
    def test_validate_payment(self, mock_post):
        """A unit test for the method for validating card payment"""
        mock_post.return_value.json.return_value = {
            'status': 'success',
            'message': 'Charge complete',
        }
        resp = TransactionServices.validate_card_payment('flwRef', 12345)
        self.assertEqual(resp['status'], 'success')

    @patch('transactions.transaction_services.requests.post')
    def test_verify_payment(self, mock_post):
        """A unit test for the method for verifying card payment"""
        mock_post.return_value.json.return_value = {
            'status': 'success',
            'message': 'Charge complete',
        }
        resp = TransactionServices.verify_payment('flwRef')
        self.assertEqual(resp['status'], 'success')

    def test_save_card_when_not_requested(self):
        """
        A unit test for what happened if the user does not request that
        their card be tokenized.
        """
        payload = {'data': {
            'tx': {'txRef': 'sampletxref'}, 'meta': [{'metavalue': 0}],
            'vbvmessage': 'somemessage', 'status': 'successful',
            'custemail': 'email@email.com', 'card': {
                'expirymonth': '11', 'expiryyear': 22, 'last4digits': 1234,
                'card_tokens': [{'embedtoken': 'sometoken'}],
                'brand': 'somebrand'}}
        }

        resp = TransactionServices.save_card(payload)
        self.assertEqual(resp, None)

    def test_save_card_with_no_exception(self):
        """
        A unit test for what happened if the user requests that
        their card be tokenized and the request is successful.
        """
        payload = {'data': {
            'tx': {'txRef': 'sampletxref'}, 'meta': [{'metavalue': 1}],
            'vbvmessage': 'somemessage', 'status': 'successful',
            'custemail': 'email@email.com', 'card': {
                'expirymonth': '11', 'expiryyear': 22, 'last4digits': 1234,
                'card_tokens': [{'embedtoken': 'sometoken'}],
                'brand': 'somebrand'}}
        }

        resp = TransactionServices.save_card(payload)
        self.assertEqual(resp, '. Card details have been saved.')

    @patch('transactions.transaction_services.User.active_objects.filter')
    def test_save_card_with_exception(self, mock_filter):
        """
        A unit test for what happened if the user requests that
        their card be tokenized and the request is not successful.
        """
        payload = {'data': {
            'tx': {'txRef': 'sampletxref'}, 'meta': [{'metavalue': 1}],
            'vbvmessage': 'somemessage', 'status': 'successful',
            'custemail': 'email@email.com', 'card': {
                'expirymonth': '11', 'expiryyear': 22, 'last4digits': 1234,
                'card_tokens': [{'embedtoken': 'sometoken'}],
                'brand': 'somebrand'}}
        }
        mock_filter.side_effect = User.DoesNotExist

        resp = TransactionServices.save_card(payload)

        self.assertEqual(
            resp, '. Card details could not be saved. Try latter.')

    @patch('transactions.transaction_services.requests.post')
    def test_pay_with_saved_card_when_user_has_saved_card(self,
                                                          mock_post):
        """
        A unit test for the method that handles actual saving of card
        details.
        """
        payload = {
            "status": "success",
            "message": "Charge success",
            "data": {
                "id": 124983,
                "txRef": "MC_1522966555872",
                "orderRef": None,
                "flwRef": "FLW-M03K-3705232bce4536328b24d03579365e9f", }}
        mock_post.return_value.json.return_value = payload
        test_user = UserFactory.create()
        card = CardInfoFactory.create(user_id=test_user.id)

        resp = TransactionServices.pay_with_saved_card(test_user, 1000, card)
        self.assertIn('data', resp)

    def test_save_already_saved_card(self):
        """
        A unit test for what happened if the user requests to
        save already saved card
        """

        resp = TransactionServices.save_card(self.payload)
        resp = TransactionServices.save_card(self.payload)
        self.assertEqual(resp, '. Card already saved.')
