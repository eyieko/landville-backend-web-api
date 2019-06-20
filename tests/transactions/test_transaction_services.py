"""Module of tests for TransactionServices helper class."""
from django.test import SimpleTestCase
from faker import Factory
from unittest.mock import patch
from transactions.transaction_services import TransactionServices


class TransactionServicesTest(SimpleTestCase):

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
