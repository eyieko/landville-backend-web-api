from tests.transactions import BaseTest
from transactions.views import ClientAccountAPIView
from rest_framework import status
from django.urls import reverse
from rest_framework.test import force_authenticate
from faker.providers.credit_card import Provider
from transactions.serializers import (CardPaymentSerializer,
                                      TransactionSerializer,
                                      PaymentValidationSerializer)
from faker import Faker

ACCOUNT_DETAIL_URL = reverse("transactions:all-accounts")


def single_detail_url(account_number):
    return reverse("transactions:single-account", args=[account_number])


class TestSerializers(BaseTest):

    fake_credit_generator = Faker()
    fake_credit = Provider(generator=fake_credit_generator)
    data = {
        "cardno": fake_credit.credit_card_number(),
        "cvv": fake_credit.credit_card_security_code(),
        "expirymonth": fake_credit.credit_card_expire().split('/')[0],
        "expiryyear": fake_credit.credit_card_expire().split('/')[1],
        "amount": 8800.00,
        "billingzip": "07205",
        "billingcity": "billingcity",
        "billingaddress": "billingaddress",
        "billingstate": "NJ",
        "billingcountry": "UK"
    }
    otp_data = {
        'flwRef': 'FLW-MOCK-c189daaf7570c7522adaccd9e2f752ce',
        'otp': 12345,
    }

    def test_error_when_you_post_with_invalid_account_number(self):
        """ you get an error when you
        upload with an a non interger acc number"""

        view = ClientAccountAPIView.as_view()

        request = self.factory.post(
            ACCOUNT_DETAIL_URL, self.invalid_details, format='json')
        force_authenticate(request, user=self.user1,
                           token=None)
        resp = view(request)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'Your account number must be 10 digits and only intergers',
            str(resp.data))

    def test_error_when_you_post_with_invalid_swift_code(self):
        """ you get an error when you upload with an
        a non letter swift code """

        view = ClientAccountAPIView.as_view()

        request = self.factory.post(
            ACCOUNT_DETAIL_URL, self.invalid_swift_code, format='json')
        force_authenticate(request, user=self.user1,
                           token=None)
        resp = view(request)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'Swift code must only be letters characters', str(resp.data))

    def test_serializer_raise_an_error_if_no_purpose(self):
        serializer = CardPaymentSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('purpose', serializer.errors.keys())
        self.assertEquals(str(serializer.errors.get('purpose')[0]),
                          'This field is required.')

    def test_payment_serializer_raise_an_error_if_invalid_purpose(self):
        """
        tes if the serializer raise an error with data with invalid purpose
        """
        invalid_data = self.data.copy()
        invalid_data['purpose'] = 'Espoir'
        serializer = CardPaymentSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('purpose', serializer.errors.keys())
        self.assertIn('is not a valid choice',
                      str(serializer.errors.get('purpose')[0]))

    def test_payment_serializer_works_when_purpose_valid(self):
        """
        test if the serializer works with valid data
        """
        invalid_data = self.data.copy()
        invalid_data['purpose'] = 'Saving'
        serializer = CardPaymentSerializer(data=invalid_data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_raise_an_error_if_no_property_id(self):
        """
        test if serializer raise an error id purpose is buying and the property
        id is not found
        """
        valid_data = self.data.copy()
        valid_data['purpose'] = 'Buying'
        serializer = CardPaymentSerializer(data=valid_data)
        self.assertFalse(serializer.is_valid())

    def test_payment_serializer_raise_an_error_if_invalid_property_id(self):
        """
        test if the serializer raise an error if data has invalid property id
        """
        invalid_data = self.data.copy()
        invalid_data['purpose'] = 'Buying'
        invalid_data['property_id'] = 'Espoir'
        serializer = CardPaymentSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('property_id', serializer.errors.keys())
        self.assertEquals(str(serializer.errors.get('property_id')[0]),
                          'A valid integer is required.')

    def test_payment_serializer_works_when_property_valid(self):
        """
        test if serializer work with valid property id
        """
        valid_data = self.data.copy()
        valid_data['property_id'] = 1
        valid_data['purpose'] = 'Buying'
        serializer = CardPaymentSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

    def test_all_deposit_serializer_works(self):
        """
        test if get all deposit serializer works
        """
        transaction = self.create_transaction()
        serialized_transaction_data = TransactionSerializer(transaction)
        self.assertIsNotNone(serialized_transaction_data)

    def test_pin_validation_serializer_failed(self):
        """
        test if pin validation serializer failed with no purpose
        """
        serializer = PaymentValidationSerializer(data=self.otp_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('purpose', serializer.errors.keys())
        self.assertEquals(str(serializer.errors.get('purpose')[0]),
                          'This field is required.')

    def test_pin_validation_serializer(self):
        """
        test if pin validation serializer works
        """
        otp_data = self.otp_data.copy()
        otp_data['property_id'] = 1
        otp_data['purpose'] = 'Buying'
        serializer = PaymentValidationSerializer(data=otp_data)
        self.assertTrue(serializer.is_valid())
