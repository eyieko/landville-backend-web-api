from mock import patch
from django.test import TestCase
from rest_framework import serializers

from tests.factories.authentication_factory import UserFactory, ClientFactory
from tests.factories.property_factory import PropertyFactory
from transactions.models import ClientAccount
from authentication.models import User
from property.models import Property
from utils import managers, client_permissions, BaseUtils


class CustomManagerTest(TestCase):
    """This class contains tests for the custom managers"""

    def setUp(self):
        self.user1 = UserFactory.create()
        self.user2 = UserFactory.create()
        self.client1 = ClientFactory.create(
            client_admin=self.user1, approval_status="approved")
        self.client2 = ClientFactory.create(client_name='Hank Green And CO',
                                            phone='3452435423523',
                                            client_admin=self.user2,
                                            approval_status="approved")
        self.property1 = PropertyFactory.create(client=self.client1)
        self.property2 = PropertyFactory.create(client=self.client2)

    def test_that_we_can_use_custom_query_to_get_all_active_users(self):
        users = User.active_objects.all_objects()
        self.assertEqual(len(users), 2)

    def test_that_we_can_query_for_property_owned_by_specific_user(self):
        client1_properties = Property.active_objects.for_client(
            client=self.client1)
        self.assertEqual(client1_properties.first(), self.property1)

    def test_that_we_can_search_property_by_slug(self):
        slug = self.property2.slug
        query = Property.active_objects.by_slug(slug)
        self.assertEqual(len(query), 1)
        self.assertEqual(query.first(), self.property2)

    def test_that_we_can_filter_published_property(self):
        property3 = PropertyFactory.create(client=self.client2)
        property3.is_published = True
        property3.save()
        query = Property.active_objects.all_published()
        self.assertEqual(len(query), 1)
        self.assertEqual(query.first(), property3)

    def test_that_we_can_filter_sold_property(self):
        property3 = PropertyFactory.create(client=self.client2)
        property3.is_sold = True
        property3.save()
        query = Property.active_objects.all_sold()
        self.assertEqual(len(query), 1)
        self.assertEqual(query.first(), property3)

    @patch.object(managers.ClientAccountQuery, 'client_admin_has_client')
    def test_client_admin_has_client_is_true(
            self, mock_client_admin_has_client):
        mock_client_admin_has_client.return_value = True
        client_account_instance = managers.ClientAccountQuery()
        result = client_account_instance.client_admin_has_client('fake-id')
        self.assertTrue(result)

    @patch('utils.managers.ClientAccountQuery')
    def test_mock_client_account_query(self, MockClientAccountQuery):
        managers.ClientAccountQuery()
        assert MockClientAccountQuery is managers.ClientAccountQuery
        assert MockClientAccountQuery.called

    def test_has_permission_with_get(self):
        with patch.object(client_permissions.IsClient,
                          'has_permission', return_value=False) as mock_method:
            is_client = client_permissions.IsClient()
            is_client.has_permission(
                {
                    'method': 'GET',
                    'request': {
                        'user': {
                            'is_authenticated': True
                        }
                    }
                }, 'a fake_view')
            mock_method.assert_called_once_with(
                {
                    'method': 'GET',
                    'request': {
                        'user': {
                            'is_authenticated': True
                        }
                    }
                }, 'a fake_view')

    def test_client_admin_has_client(self):
        user = UserFactory(role="CA", email="test@gmail.com")
        client1 = ClientFactory(client_admin=user)
        account_owner = ClientAccount.active_objects.client_admin_has_client(
            client1.client_admin.id)
        self.assertIsNotNone(account_owner)
