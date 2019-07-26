"""Module of tests for views of transactions app."""
import json
from tests.transactions import BaseTest
from transactions.views import (
    ClientAccountAPIView,
    RetreiveTransactionsAPIView
)
from django.urls import reverse
from rest_framework.test import force_authenticate
from rest_framework.views import status
from faker import Factory
from unittest.mock import patch
from tests.factories.authentication_factory import UserFactory, ClientFactory
from tests.factories.transaction_factory import TransactionFactory
from ..factories.property_factory import PropertyFactory
from transactions.serializers import DepositSerializer
from transactions.models import Deposit
from transactions.views import RetrieveDepositsApiView
from ..factories.transaction_factory import SavingsFactory
from transactions.transaction_utils import save_deposit
from .test_utils import references
from django.db.models import Q


ACCOUNT_DETAIL_URL = reverse("transactions:all-accounts")
# url to access the GET transactions endpoint
USER_TRANSACTIONS_URL = reverse("transactions:transactions")


def single_detail_url(account_number):
    return reverse("transactions:single-account", args=[account_number])


class TestClientAccountDetailsViews(BaseTest):

    def test_user_must_have_client_to_post_account_details(self):
        view = ClientAccountAPIView.as_view()
        self.user3.role = 'CA'
        self.user3.save()
        request = self.factory.post(
            ACCOUNT_DETAIL_URL, self.acc_details3, format='json')
        force_authenticate(request, user=self.user3)
        res = view(request)
        self.assertIn(
            'you must have a client company to submit account details',
            str(res.data)
        )

    def test_staff_can_get_even_deleted_account_details(self):
        """ a staff can get even deleted items """
        view = ClientAccountAPIView.as_view()
        request = self.factory.post(
            ACCOUNT_DETAIL_URL, self.account_details, format='json')
        force_authenticate(request, user=self.user1)
        res = view(request)
        account_number = res.data['account_number']
        self.factory.delete(
            single_detail_url(account_number), format='json')
        request3 = self.factory.get(
            single_detail_url(account_number), format='json')
        self.user2.role = 'LA'
        self.user2.save()
        force_authenticate(request3, user=self.user2)

        res = self.view2(request3, account_number=account_number)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_view_all_details_successfully(self):
        """ client admin view all the details successfully """

        view = ClientAccountAPIView.as_view()
        request = self.factory.post(
            ACCOUNT_DETAIL_URL, self.account_details, format='json')
        force_authenticate(request, user=self.user1)
        view(request)

        request2 = self.factory.get(ACCOUNT_DETAIL_URL)
        self.user1.role = 'CA'
        self.user1.save()
        force_authenticate(request2, user=self.user1)
        resp2 = view(request2)

        self.assertEqual(resp2.status_code, status.HTTP_200_OK)

    def test_staff_gets_the_correct_message_no_details_posted(self):
        """
        staff should be able to get the right details when no details
        are posted
        """

        view = ClientAccountAPIView.as_view()
        request = self.factory.get(ACCOUNT_DETAIL_URL)
        self.user3.role = 'LA'
        self.user3.save()
        force_authenticate(request, user=self.user3)
        resp = view(request)
        self.assertIn(
            'There are no details posted by any client so far', str(resp.data))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_success_details_uploaded(self):
        """ test successfully upload your account details """

        view = ClientAccountAPIView.as_view()

        request = self.factory.post(
            ACCOUNT_DETAIL_URL, self.account_details, format='json')
        force_authenticate(request, user=self.user1,
                           token=None)
        resp = view(request)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_client_admin_gets_the_appropriate_message_no_records_posted(self):
        """ client admin can be able to only view the accounts """
        view = ClientAccountAPIView.as_view()

        request2 = self.factory.get(
            ACCOUNT_DETAIL_URL, format='json')
        force_authenticate(request2, user=self.user1)

        res = view(request2)
        self.assertIn("You have no account details posted", str(res.data))

    def test_get_one_account(self):
        """ test when viewing one specific account """
        view = ClientAccountAPIView.as_view()
        request = self.factory.post(
            ACCOUNT_DETAIL_URL, self.account_details, format='json')
        force_authenticate(request, user=self.user1)
        actual_res = view(request)
        account_number = actual_res.data['account_number']

        request2 = self.factory.get(
            single_detail_url(account_number), format='json')
        force_authenticate(request2, user=self.user4)

        res = self.view2(request2, account_number=account_number)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_not_existing_account_details(self):
        """ test for account details not found """
        view = ClientAccountAPIView.as_view()

        request = self.factory.post(
            ACCOUNT_DETAIL_URL, self.account_details, format='json')
        force_authenticate(request, user=self.user1)
        view(request)
        account_number = 'djsdjshdsjdhskddkjwfsjkdfeghfjkas'
        request2 = self.factory.get(
            single_detail_url(account_number), format='json')
        force_authenticate(request2, user=self.user1)

        res = self.view2(request2, account_number=account_number)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_account_details(self):
        """ test for deleting account details """
        view = ClientAccountAPIView.as_view()

        request = self.factory.post(
            ACCOUNT_DETAIL_URL, self.account_details, format='json')
        force_authenticate(request, user=self.user1)
        actual_res = view(request)
        account_number = actual_res.data['account_number']

        request2 = self.factory.delete(
            single_detail_url(account_number), format='json')
        force_authenticate(request2, user=self.user1)

        res = self.view2(request2, account_number=account_number)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('Account details successfully deleted', str(res.data))

    def test_delete_account_details_non_existent(self):
        """ test that non existent details won't be found while deleting """

        account_number = 'shdskdhsdhsdjsdkashdksjdhkddj'

        request2 = self.factory.delete(
            single_detail_url(account_number), format='json')
        force_authenticate(request2, user=self.user1)

        res = self.view2(request2, account_number=account_number)

        self.assertIn('No ClientAccount', str(res.data))

    def test_update_account_details(self):
        """ test account details updated successfully """

        view = ClientAccountAPIView.as_view()

        request = self.factory.post(
            ACCOUNT_DETAIL_URL, self.account_details, format='json')
        force_authenticate(request, user=self.user1)
        actual_res = view(request)
        account_number = actual_res.data['account_number']

        request2 = self.factory.put(
            single_detail_url(account_number), self.account_details,
            format='json')
        force_authenticate(request2, user=self.user1)

        res = self.view2(request2, account_number=account_number)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_account_details_not_found(self):
        """ account details that cannot be found can't be updated """

        account_number = 'ksjdksjdksjdksjdksjdsdsdsjdsjsdjk'

        request2 = self.factory.put(
            single_detail_url(account_number), self.account_details2,
            format='json')
        force_authenticate(request2, user=self.user1)

        res = self.view2(request2, account_number=account_number)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_details_no_permission(self):
        """you can't post without the correct credentialsi.e without login """

        res = self.client.post(ACCOUNT_DETAIL_URL,
                               self.account_details, format='json')

        result = json.loads(res.content)
        self.assertIn(
            'Please log in to proceed.', str(result))

    def test_account_number_must_be_unique(self):
        """ test that an account shoudl be unique """

        view = ClientAccountAPIView.as_view()
        request = self.factory.post(
            ACCOUNT_DETAIL_URL, self.account_details, format='json')
        force_authenticate(request, user=self.user1)

        view(request)

        request2 = self.factory.post(
            ACCOUNT_DETAIL_URL, self.account_details, format='json')
        force_authenticate(request2, user=self.user1)

        actual_response = view(request2)

        self.assertEqual(actual_response.status_code,
                         status.HTTP_400_BAD_REQUEST)


class CardPaymentTest(BaseTest):

    def setUp(self):
        self.card_pin_url = reverse('transactions:card_pin')
        self.auth_user = UserFactory(is_verified=True)
        self.land_client = ClientFactory.create(client_admin=self.auth_user)
        self.property = PropertyFactory.create(client=self.land_client)
        self.transaction = TransactionFactory.\
            create(target_property=self.property,
                   buyer=self.auth_user,
                   amount_paid=90)
        self.card_foreign_url = reverse('transactions:card_foreign')
        self.cardless_url = reverse('transactions:tokenized_card')
        self.card_validate_url = reverse('transactions:validate_card')
        self.foreign_validate_url = reverse('transactions:validation_response'
                                            )+'?response={"txRef": "sometxref"}'  # noqa
        self.faker = Factory.create()
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.auth_user.token}'
        )
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

    @patch('transactions.transaction_services'
           '.TransactionServices.initiate_card_payment')
    @patch('transactions.transaction_services.'
           'TransactionServices.authenticate_card_payment')
    def test_payments_with_domestic_card_valid_transaction(
            self, mock_auth, mock_initiate
    ):
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
        del self.card_info['purpose']
        for url in (
                self.card_foreign_url, self.card_pin_url
        ):
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
                'tx': {'txRef': 'sampletxref'}, 'meta': [self.save_card_meta]}
        }
        mock_verify.return_value = {
            'data': {
                'tx': {'txRef': 'sampletxref'}, 'meta': [self.save_card_meta],
                'vbvmessage': 'somemessage', 'status': 'successful',
                'custemail': 'email@email.com', 'card': {'expirymonth': '11',
                                                         'expiryyear': 22, 'last4digits': 1234,  # noqa
                                                         'card_tokens': [{'embedtoken': 'sometoken'}],  # noqa
                                                         'brand': 'somebrand'}}
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
                'tx': {'txRef': 'sampletxref'},
                'meta': [self.not_save_card_meta]}
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
    def test_validate_local_payment_fail(
            self, mock_validate):
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
    def test_validate_local_payment_fail_verify_response(self,
                                                         mock_verify,
                                                         mock_validate):
        mock_verify.return_value = {
            'status': 'error',
            'data': {
                'suggested_auth': 'NOAUTH_INTERNATIONAL',
                'status': 'error'
            }
        }
        mock_validate.return_value = {
            'message': 'Charge Complete',
            'status_code': 200,
            'data': {
                'tx': {
                    'txRef': 'sampletxref',
                },
                'meta': [self.not_save_card_meta]
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

        data = {
            'flwRef': 'FLW-MOCK-c189daaf7570c7522adaccd9e2f752ce',
            'otp': 12345,
        }
        resp = self.client.post(self.card_validate_url, data)
        json_resp = resp.json()
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(json_resp.get("errors").get('purpose'),
                         ['This field is required.'])

    @patch('transactions.transaction_services'
           '.TransactionServices.verify_payment')
    def test_validate_foreign_payment_with_card_save(
            self, mock_verify):
        """
        An integrated test for the view method for validating card
        international payment if card tokenization is requested.
        """
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
                }
            }
        }

        resp = self.client.get(self.foreign_validate_url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['message'],
                         'somemessage. Card details have been saved.')

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
                'vbvmessage': 'fake fake'
            },
            'message': 'invalid transaction id'
        }

        resp = self.client.get(self.foreign_validate_url)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json().get('message'), 'invalid transaction id')

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
                'tx': {'txRef': 'sampletxref'},
                'meta': [self.not_save_card_meta]}
        }
        mock_verify.return_value = {
            'status': 'success',
            'data': {
                'tx': {'txRef': 'sampletxref'},
                'meta': [self.not_save_card_meta] + self.purpose_meta,
                'vbvmessage': 'somemessage', 'status': 'successful',
                'custemail': 'email@email.com', 'card': {
                    'expirymonth': '11', 'expiryyear': 22, 'last4digits': 1234,
                    'card_tokens': [{'embedtoken': 'sometoken'}],
                    'brand': 'somebrand'}}
        }

        resp = self.client.get(self.foreign_validate_url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['message'], 'somemessage')

    @patch('transactions.transaction_services'
           '.TransactionServices.pay_with_saved_card')
    def test_cardless_payments_with_valid_transaction(
            self, mock_saved_card):
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
        self.assertEqual(json_resp.get('errors').get('amount'),
                         ['This field is required.'])


class TestTransactions(BaseTest):

    """Tests for the user transactions functionality"""

    def test_retreive_buyer_transactions(self):
        """test to retreive user transaction detailes"""
        view = RetreiveTransactionsAPIView.as_view()
        TransactionFactory.create(
            target_property=self.property1, buyer=self.user4)
        request = self.factory.get(USER_TRANSACTIONS_URL)
        force_authenticate(request, user=self.user4)
        response = view(request)
        self.assertEqual(
            response.data['message'], "Transaction(s) retrieved successfully")
        self.assertEqual(response.status_code, 200)

    def test_retreive_client_transactions(self):
        """test to retreive all transaction detailes of a client"""
        view = RetreiveTransactionsAPIView.as_view()
        TransactionFactory.create(
            target_property=self.property1, buyer=self.user4)
        request = self.factory.get(USER_TRANSACTIONS_URL)
        force_authenticate(request, user=self.user1)
        response = view(request)
        self.assertEqual(
            response.data['message'], "Transaction(s) retrieved successfully")
        self.assertEqual(response.status_code, 200)

    def test_retreive_landville_transactions(self):
        """test to retreive all transactions in landville"""
        view = RetreiveTransactionsAPIView.as_view()
        TransactionFactory.create(
            target_property=self.property1, buyer=self.user4)
        request = self.factory.get(USER_TRANSACTIONS_URL)
        force_authenticate(request, user=self.user5)
        response = view(request)
        self.assertEqual(
            response.data['message'], "Transaction(s) retrieved successfully")
        self.assertEqual(response.status_code, 200)

    def test_buyer_cant_retreive_other_buyers_transactions(self):
        """test to retreive other users transaction detailes"""
        view = RetreiveTransactionsAPIView.as_view()
        TransactionFactory.create(
            target_property=self.property1, buyer=self.user4)
        request = self.factory.get(USER_TRANSACTIONS_URL)
        force_authenticate(request, user=self.user6)
        response = view(request)
        self.assertEqual(response.data['errors'], "No transactions available")
        self.assertEqual(response.status_code, 404)

    def test_retreive_transactions_of_user_with_zero_transactions(self):
        """
        test to retreive user transaction detailes where user has no
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


class TestReturnAllMyDeposit(BaseTest):
    def test_should_return_all_my_deposit(self):
        """
        This test ensure that I can get all my deposit
        """
        amount_to_save = 100
        savings = SavingsFactory.create(owner=self.user4)
        deposit, saving_updated = save_deposit('Saving',
                                               references,
                                               amount_to_save,
                                               self.user4,
                                               'test test')
        request = self.factory.get(reverse("transactions:my_deposit"),
                                   format='json')
        force_authenticate(request, user=self.user4)
        view = RetrieveDepositsApiView.as_view()
        response = view(request, format='json')
        expected = Deposit.objects.select_related(
            'transaction', 'account').filter(
                Q(transaction__buyer__id=self.user4.id) |
                Q(account__owner__id=self.user4.id))
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
        deposit, saving_updated = save_deposit('Buying',
                                               references,
                                               1000,
                                               self.user4,
                                               transaction.target_property,
                                               'test test')
        request = self.factory.get(reverse("transactions:my_deposit"),
                                   format='json')
        force_authenticate(request, user=self.user1)
        view = RetrieveDepositsApiView.as_view()
        response = view(request, format='json')
        expected = Deposit.objects.select_related(
            'transaction',
            'transaction__target_property')
        expected = expected.filter(
            transaction__target_property__client_id=self.user1.employer.
            first().id)
        serialized = DepositSerializer(expected, many=True)
        results = response.data.get('results')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(results, serialized.data)
