"""Module of tests for views of transactions app."""
from tests.transactions import BaseTest
from django.urls import reverse
from rest_framework.views import status
from faker import Factory
from unittest.mock import patch
from tests.factories.authentication_factory import UserFactory, \
    ClientFactory, CardInfoFactory
from tests.factories.transaction_factory import TransactionFactory
from tests.factories.property_factory import PropertyFactory


def single_detail_url(account_number):
    return reverse("transactions:single-account", args=[account_number])


class CardPaymentTest(BaseTest):
    def setUp(self):
        self.card_pin_url = reverse('transactions:card_pin')
        self.auth_user = UserFactory(is_verified=True)
        self.card = CardInfoFactory.create(user_id=self.auth_user.id)
        self.land_client = ClientFactory.create(client_admin=self.auth_user)
        self.property = PropertyFactory.create(client=self.land_client)
        self.transaction = TransactionFactory.\
            create(target_property=self.property,
                   buyer=self.auth_user,
                   amount_paid=90)
        self.card_foreign_url = reverse('transactions:card_foreign')
        self.cardless_url = reverse(
            'transactions:tokenized_card', args=[self.card.id]
            )
        self.card_validate_url = reverse('transactions:validate_card')
        self.foreign_validate_url = reverse(
            'transactions:validation_response'
        ) + '?response={"txRef": "sometxref"}'  # noqa
        self.faker = Factory.create()
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.auth_user.token}')
        self.card_info = {
            'cardno':
            self.faker.credit_card_number(card_type=None),
            'cvv':
            self.faker.credit_card_security_code(card_type=None),
            'expirymonth':
            self.faker.credit_card_expire(start='now',
                                          end='+10y',
                                          date_format='%m'),
            'expiryyear':
            self.faker.credit_card_expire(start='now',
                                          end='+10y',
                                          date_format='%y'),
            'amount':
            20000.00,
            'purpose':
            'Buying',
            'property_id':
            self.property.id
        }
        self.address_details = {
            'billingzip': '07205',
            'billingcity': 'billingcity',
            'billingaddress': 'billingaddress',
            'billingstate': 'NJ',
            'billingcountry': 'UK'
        }
        self.save_card_meta = {'metaname': 'save_card', 'metavalue': 1}
        self.not_save_card_meta = {'metaname': 'save_card', 'metavalue': 0}
        self.purpose_meta = [{
            'metaname': 'purpose',
            'metavalue': 'Saving'
        }, {
            'metaname': 'property_id',
            'metavalue': None
        }]
        UserFactory.create(email='email@email.com')

    @patch('transactions.transaction_services'
           '.TransactionServices.initiate_card_payment')
    @patch('transactions.transaction_services.'
           'TransactionServices.authenticate_card_payment')
    def test_payments_with_domestic_card_valid_transaction(
            self, mock_auth, mock_initiate):
        mock_initiate.return_value = {
            'status': 'success',
            'data': {
                'suggested_auth': 'PIN'
            }
        }
        mock_auth.return_value = {
            'status': 'success',
            'data': {
                'flwRef': 'FLW-MOCK-9deab',
                'authModelUsed': 'PIN'
            }
        }

        self.card_info.update({'pin': 1111})
        resp = self.client.post(self.card_pin_url, self.card_info)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['message'],
                         'Kindly input the OTP sent to you')

    @patch('transactions.transaction_services'
           '.TransactionServices.initiate_card_payment')
    def test_payments_with_domestic_card_invalid_transaction(
            self, mock_initiate):
        """
        test if domestic card transaction failed for invalid error
        """
        mock_initiate.return_value = {
            "status": "error",
            "data": {
                "suggested_auth": "PIN"
            }
        }

        self.card_info.update({'pin': 1111})

        resp = self.client.post(self.card_pin_url, self.card_info)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data.get('message'), None)

    @patch('transactions.transaction_services'
           '.TransactionServices.initiate_card_payment')
    @patch('transactions.transaction_services'
           '.TransactionServices.authenticate_card_payment')
    def test_payments_with_domestic_card_failed_authentication(
            self, mock_auth, mock_initiate):
        """
        test the case where it fails to authenticated domestic card
        """
        mock_initiate.return_value = {
            "status": "success",
            "data": {
                "suggested_auth": "PIN"
            }
        }
        mock_auth.return_value = {
            'status': 'error',
            'data': {
                'flwRef': 'FLW-MOCK-9deab',
                'authModelUsed': 'PIN'
            }
        }

        self.card_info.update({'pin': 1111})

        resp = self.client.post(self.card_pin_url, self.card_info)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data.get('message'), None)

    def test_payments_with_domestic_card_failed_serializer_validation(self):
        """
        test if domestic  card payment serializer  failed to validate data
        """

        del self.card_info['cardno']
        self.card_info.update({'pin': 1111})
        resp = self.client.post(self.card_pin_url, self.card_info)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data['cardno'], ['This field is required.'])

    @patch('transactions.transaction_services'
           '.TransactionServices.initiate_card_payment')
    @patch('transactions.transaction_services'
           '.TransactionServices.authenticate_card_payment')
    def test_international_payments_with_valid_transaction(
            self, mock_auth, mock_initiate):
        """
        test success for international payment
        """
        mock_initiate.return_value = {
            'status': 'success',
            'message': 'AUTH_SUGGESTION',
            'data': {
                'suggested_auth': 'NOAUTH_INTERNATIONAL'
            }
        }

        mock_auth.return_value = {
            'status': 'success',
            'data': {
                'authurl': 'authurl',
                'authModelUsed': 'NOAUTH_INTERNATIONAL',
                'txRef': 'tetteeteteteet'
            }
        }

        self.card_info.update(self.address_details)
        for purpose in ['Saving', 'Buying']:
            card_data = self.card_info.copy()
            card_data['purpose'] = purpose
            resp = self.client.post(self.card_foreign_url, card_data)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.data.get('message'), 'authurl')
            self.assertEqual(resp.data.get('txRef'), "tetteeteteteet")

    @patch('transactions.transaction_services'
           '.TransactionServices.initiate_card_payment')
    def test_international_payments_with_invalid_transaction(
            self, mock_initiate):
        """
        test failure of international payments due to invalid transactions
        """
        mock_initiate.return_value = {
            'status': 'error',
            'data': {
                'suggested_auth': 'NOAUTH_INTERNATIONAL'
            }
        }

        self.card_info.update(self.address_details)
        resp = self.client.post(self.card_foreign_url, self.card_info)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data.get('message'), None)

    @patch('transactions.transaction_services'
           '.TransactionServices.initiate_card_payment')
    @patch('transactions.transaction_services'
           '.TransactionServices.authenticate_card_payment')
    def test_international_payments_with_failed_authentication(
            self, mock_auth, mock_initiate):
        """
        test failure of international payments due to invalid authentication
        """
        mock_initiate.return_value = {
            'status': 'success',
            'message': 'AUTH_SUGGESTION',
            'data': {
                'suggested_auth': 'NOAUTH_INTERNATIONAL'
            }
        }
        mock_auth.return_value = {
            'status': 'error',
            'message': 'error message'
        }

        self.card_info.update(self.address_details)
        resp = self.client.post(self.card_foreign_url, self.card_info)
        self.assertEqual(resp.status_code, 400)

    def test_international_payments_failed_serializer_validation(self):
        """
        test failure of international payments due invalid data send
        """
        del self.card_info['cardno']
        resp = self.client.post(self.card_foreign_url, self.card_info)
        json_resp = resp.json()
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(json_resp['cardno'], ['This field is required.'])

    def test_should_return_error_if_property_not_found(self):
        """
        Check if an error is returned if a property we are buying is not
        found
        """
        invalid_card_infos = self.card_info
        invalid_card_infos['purpose'] = 'Buying'
        invalid_card_infos['property_id'] = 199
        invalid_card_infos.update(self.address_details)
        resp = self.client.post(self.card_foreign_url, invalid_card_infos)
        json_resp = resp.json()
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(json_resp.get('errors'),
                         'No Property matches the given query.')

    def test_payments_failed_no_purpose(self):
        """
        test failure of international payments due to no purpose
        """
        del self.card_info['purpose']
        for url in (self.card_foreign_url, self.card_pin_url):
            resp = self.client.post(url, self.card_info)
            json_resp = resp.json()
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(json_resp['purpose'], ['This field is required.'])

    @patch('transactions.transaction_services'
           '.TransactionServices.verify_payment')
    @patch('transactions.transaction_services'
           '.TransactionServices.validate_card_payment')
    def test_valid_pin_payment(self, mock_validate, mock_verify):
        """
        An integrated test for the view method for validating card PIN
        payment if card tokenization is requested.
        """
        mock_validate.return_value = {
            'message': 'Charge Complete',
            'status_code': 200,
            'data': {
                'tx': {
                    'txRef': 'sampletxref'
                },
                'meta': [self.save_card_meta]
            }
        }
        mock_verify.return_value = {
            'data': {
                'tx': {
                    'txRef': 'sampletxref'
                },
                'meta': [self.save_card_meta],
                'vbvmessage': 'somemessage',
                'status': 'successful',
                'custemail': 'email@email.com',
                'card': {
                    'expirymonth': '11',
                    'expiryyear': 22,
                    'last4digits': 1234,  # noqa
                    'card_tokens': [{
                        'embedtoken': 'sometoken'
                    }],  # noqa
                    'brand': 'somebrand'
                },
            }
        }

        data = {
            'flwRef': 'FLW-MOCK-c189daaf7570c7522adaccd9e2f752ce',
            'otp': 12345,
            'purpose': 'Saving',
        }

        resp = self.client.post(self.card_validate_url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['message'], 'Charge Complete')

    @patch('transactions.transaction_services'
           '.TransactionServices.verify_payment')
    @patch('transactions.transaction_services'
           '.TransactionServices.validate_card_payment')
    def test_valid_PIN_payment_no_card_save(self, mock_validate, mock_verify):
        """
        An integrated test for the view method for validating card PIN
        payment if card tokenization is not requested.
        """
        mock_validate.return_value = {
            'message': 'Charge Complete',
            'status_code': 200,
            'data': {
                'tx': {
                    'txRef': 'sampletxref'
                },
                'meta': [self.not_save_card_meta]
            }
        }
        mock_verify.return_value = {
            'data': {
                'tx': {
                    'txRef': 'sampletxref'
                },
                'meta': [self.not_save_card_meta],
                'vbvmessage': 'somemessage',
                'status': 'successful',
                'custemail': 'email@email.com',
                'card': {
                    'expirymonth': '11',
                    'expiryyear': 22,
                    'last4digits': 1234,
                    'card_tokens': [{
                        'embedtoken': 'sometoken'
                    }],
                    'brand': 'somebrand'
                }
            }
        }
        data = {
            'flwRef': 'FLW-MOCK-c189daaf7570c7522adaccd9e2f752ce',
            'otp': 12345,
        }
        for purpose in ('Buying', 'Saving'):
            data['purpose'] = purpose
            if purpose == 'Buying':
                transaction = self.create_transaction()
                data['property_id'] = transaction.target_property.id
            resp = self.client.post(self.card_validate_url, data)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.data['message'], 'Charge Complete')

    @patch('transactions.transaction_services'
           '.TransactionServices.validate_card_payment')
    def test_validate_local_payment_fail(self, mock_validate):
        """
        test failure of validation for local payment
        """
        mock_validate.return_value = {
            'status': 'error',
            'data': {
                'suggested_auth': 'NOAUTH_INTERNATIONAL'
            }
        }
        data = {
            'flwRef': 'FLW-MOCK-c189daaf7570c7522adaccd9e2f752ce',
            'otp': 12345,
        }
        for purpose in ('Buying', 'Saving'):
            data['purpose'] = purpose
            if purpose == 'Buying':
                transaction = self.create_transaction()
                data['property_id'] = transaction.target_property.id
            resp = self.client.post(self.card_validate_url, data)
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(resp.data.get('message'), None)

    @patch('transactions.transaction_services'
           '.TransactionServices.validate_card_payment')
    @patch('transactions.transaction_services'
           '.TransactionServices.verify_payment')
    def test_validate_local_payment_fail_verify_response(
            self, mock_verify, mock_validate):
        """
        test failure of validation for local payment failed to verify response
        """
        mock_verify.return_value = {
            'status': 'error',
            'data': {
                'suggested_auth': 'NOAUTH_INTERNATIONAL',
                'status': 'error',
                'custemail': 'email@email.com'
            }
        }
        mock_validate.return_value = {
            'message': 'Charge Complete',
            'status_code': 200,
            'data': {
                'tx': {
                    'txRef': 'sampletxref',
                },
                'meta': [self.not_save_card_meta],

            }
        }

        data = {
            'flwRef': 'FLW-MOCK-c189daaf7570c7522adaccd9e2f752ce',
            'otp': 12345,
        }
        for purpose in ('Buying', 'Saving'):
            data['purpose'] = purpose
            if purpose == 'Buying':
                transaction = self.create_transaction()
                data['property_id'] = transaction.target_property.id
            resp = self.client.post(self.card_validate_url, data)
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(resp.data.get('message'), None)

    def test_pin_validation_failed_no_purpose(self):
        """
        test failure of pin validation with no purpose
        """
        data = {
            'flwRef': 'FLW-MOCK-c189daaf7570c7522adaccd9e2f752ce',
            'otp': 12345,
        }
        resp = self.client.post(self.card_validate_url, data)
        json_resp = resp.json()
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(
            json_resp.get("errors").get('purpose'),
            ['This field is required.'])

    @patch('transactions.transaction_services'
           '.TransactionServices.verify_payment')
    def test_validate_foreign_payment_with_card_save(self, mock_verify):
        """
        An integrated test for the view method for validating card
        international payment if card tokenization is requested.
        """
        for purpose in ['Saving', 'Buying']:
            self.purpose_meta[0]['metavalue'] = purpose
            if purpose == 'Buying':
                transaction = self.create_transaction()
                self.purpose_meta[1]['metavalue'] = transaction\
                    .target_property.id
            mock_verify.return_value = {
                'status': 'success',
                'data': {
                    'tx': {
                        'txRef': 'sampletxref'
                    },
                    'meta': [self.save_card_meta] + self.purpose_meta,
                    'vbvmessage': 'somemessage',
                    'status': 'successful',
                    'custemail': 'email@email.com',
                    'card': {
                        'expirymonth': '11',
                        'expiryyear': 22,
                        'last4digits': 1234,
                        'card_tokens': [{
                            'embedtoken': 'sometoken'
                        }],
                        'brand': 'somebrand'
                    },
                }
            }

            resp = self.client.get(self.foreign_validate_url)
            self.assertEqual(resp.status_code, 302)

    @patch('transactions.transaction_services'
           '.TransactionServices.verify_payment')
    def test_validate_foreign_payment_with_card_save_failed(self, mock_verify):
        """
        An integrated test for the view method for validating card
        international payment if card tokenization is requested.
        """
        mock_verify.return_value = {
            'data': {
                'tx': {
                    'txRef': 'sampletxref'
                },
                'meta': [self.save_card_meta] + self.purpose_meta,
                'status': 'error',
                'vbvmessage': 'fake fake',
                'custemail': 'email@email.com'
            },
            'message': 'invalid transaction id'
        }

        resp = self.client.get(self.foreign_validate_url)
        self.assertEqual(resp.status_code, 302)

    @patch('transactions.transaction_services'
           '.TransactionServices.verify_payment')
    @patch('transactions.transaction_services'
           '.TransactionServices.validate_card_payment')
    def test_validate_foreign_payment_no_card_save(self, mock_validate,
                                                   mock_verify):
        """
        An integrated test for the view method for validating card
        international payment if card tokenization is not requested.
        """
        mock_validate.return_value = {
            'message': 'Charge Complete',
            'status_code': 200,
            'data': {
                'tx': {
                    'txRef': 'sampletxref'
                },
                'meta': [self.not_save_card_meta]
            }
        }
        mock_verify.return_value = {
            'status': 'success',
            'data': {
                'tx': {
                    'txRef': 'sampletxref'
                },
                'meta': [self.not_save_card_meta] + self.purpose_meta,
                'vbvmessage': 'somemessage',
                'status': 'successful',
                'custemail': 'email@email.com',
                'card': {
                    'expirymonth': '11',
                    'expiryyear': 22,
                    'last4digits': 1234,
                    'card_tokens': [{
                        'embedtoken': 'sometoken'
                    }],
                    'brand': 'somebrand'
                },
            }
        }

        resp = self.client.get(self.foreign_validate_url)
        self.assertEqual(resp.status_code, 302)

    @patch('transactions.transaction_services'
           '.TransactionServices.pay_with_saved_card')
    def test_cardless_payments_with_valid_transaction(self, mock_saved_card):
        """
        An integrated test for the view method for payment with tokenized card
        that is succesful
        """
        mock_saved_card.return_value = {
            'status': 'success',
            'data': {
                'status': 'successful'
            }
        }

        self.card_info.update(self.address_details)
        resp = self.client.post(self.cardless_url, self.card_info)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['message'], 'successful')

    @patch('transactions.serializers.CardlessPaymentSerializer')
    def test_cardless_payments_with_failed_serialization(
            self, mock_serializer):
        """
        An integrated test for the view method for payment with tokenized card
        that is not successful
        """
        mock_serializer.return_value.is_valid.return_value = False
        resp = self.client.post(self.cardless_url)
        json_resp = resp.json()
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(
            json_resp.get('errors').get('amount'), ['This field is required.'])
