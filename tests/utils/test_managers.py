
from django.test import TestCase

from tests.factories.authentication_factory import UserFactory, ClientFactory
from tests.factories.property_factory import PropertyFactory
from authentication.models import User
from property.models import Property


class CustomManagerTest(TestCase):
    """This class contains tests for the custom managers"""

    def setUp(self):
        self.user1 = UserFactory.create()
        self.user2 = UserFactory.create()
        self.client1 = ClientFactory.create(
            client_admin=self.user1, approval_status="approved")
        self.client2 = ClientFactory.create(
            client_name='Hank Green And CO', phone='3452435423523', client_admin=self.user2, approval_status="approved")
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
