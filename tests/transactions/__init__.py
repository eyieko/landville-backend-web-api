import json
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from tests.factories.authentication_factory import ClientFactory, UserFactory
from tests.factories.property_factory import PropertyFactory
from transactions.views import ClientAccountAPIView, RetrieveUpdateDeleteAccountDetailsAPIView


class BaseTest(APITestCase):

    def setUp(self):
        self.user1 = UserFactory.create(role='CA')
        self.user2 = UserFactory.create(role='CA')
        self.user3 = UserFactory.create(role='CA')
        self.user4 = UserFactory.create(role='BY')
        self.user5 = UserFactory.create(role='LA')
        self.user6 = UserFactory.create(role='BY')
        self.client1 = ClientFactory.create(client_admin=self.user1)
        self.client2 = ClientFactory.create(client_admin=self.user2)
        self.property1 = PropertyFactory.create(client=self.client1)

        self.account_details = {
            'owner': self.client1.pk,
            'bank_name': 'Equity',
            'account_number': '4444444444',
            'swift_code': 'aubameyang'
        }
        self.account_details2 = {
            'owner': self.client1.pk,
            'bank_name': 'Equity',
            'account_number': '4444444444',
            'swift_code': 'aubameyang'
        }
        self.acc_details = {
            'owner': self.user1.pk,
            'bank_name': 'Equity',
            'account_number': '4444444444',
            'swift_code': 'aubameyang'
        }

        self.acc_details3 = {
            'owner': self.user3.pk,
            'bank_name': 'Equity',
            'account_number': '4444444444',
            'swift_code': 'aubameyang'
        }

        self.invalid_details = {
            'owner': self.client1.pk,
            'bank_name': 'Equity',
            'account_number': 'djkjdkjwjwjwjwjdwj',
            'swift_code': 'kelvin'
        }

        self.invalid_swift_code = {
            'owner': self.client1.pk,
            'bank_name': 'Equity',
            'account_number': '4444444444',
            'swift_code': '3463kelvin'
        }
        self.factory = APIRequestFactory()
        self.view2 = RetrieveUpdateDeleteAccountDetailsAPIView.as_view()
