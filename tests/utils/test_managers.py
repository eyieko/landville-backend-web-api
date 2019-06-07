from django.test import TestCase

from ..factories.authentication_factory import UserFactory, ClientFactory
from ..factories.property_factory import PropertyFactory
from authentication.models import User
from property.models import Property


class CustomManagerTest(TestCase):
    """This class contains tests for the custom managers"""

    def setUp(self):
        self.user1 = UserFactory.create()
        self.user2 = UserFactory.create()
        self.client1 = ClientFactory.create(client_admin=self.user1)
        self.property1 = PropertyFactory.create(client=self.client1)

    def test_that_we_can_use_custom_query_to_get_all_active_users(self):
        users = User.active_objects.all_objects()
        self.assertEqual(len(users), 2)

    def test_that_we_can_query_for_property_owned_by_specific_user(self):
        client1_properties = Property.active_objects.all_property_for_client(
            client=self.client1)
        self.assertEqual(client1_properties.first(), self.property1)
