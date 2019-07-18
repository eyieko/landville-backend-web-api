"""Module of tests for TransactionServices helper class."""
from django.test import TestCase
from faker import Factory
from unittest.mock import patch
from transactions.transaction_services import TransactionServices
from tests.factories.authentication_factory import UserFactory
from authentication.models import User


class TestTransactionServices(TestCase):

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

    @patch('transactions.transaction_services.requests.post')
    def test_initiate_payment(self, mock_post):

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
        mock_post.return_value.json.return_value = {
            'status': 'success',
            'message': 'Charge complete',
        }
        resp = TransactionServices.validate_card_payment('flwRef', 12345)
        self.assertEqual(resp['status'], 'success')

    @patch('transactions.transaction_services.requests.post')
    def test_verify_payment(self, mock_post):
        mock_post.return_value.json.return_value = {
            'status': 'success',
            'message': 'Charge complete',
        }
        resp = TransactionServices.verify_payment('flwRef')
        self.assertEqual(resp['status'], 'success')

    def test_save_card_when_not_requested(self):
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

    def test_pay_with_saved_card(self):
        test_user = UserFactory.create(card_info={
            'embedtoken': 'embedtoken',
            'card_number': '123456789',
            'card_expiry': '11/22',
            'card_brand': 'card_brand'

        })

        resp = TransactionServices.pay_with_saved_card(test_user, 1000)
        self.assertIn('data', resp)
