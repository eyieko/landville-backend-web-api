from django.test import TestCase

from property.models import Property
from tests.factories.property_factory import (
    PropertyFactory, PropertyEnquiryFactory, PropertyReviewFactory,
    PropertyInspectionFactory
)
from tests.factories.authentication_factory import UserFactory, ClientFactory


class PropertyModelTest(TestCase):
    """This class defines tests for the Property model"""

    def setUp(self):
        self.user1 = UserFactory.create()
        self.client1 = ClientFactory.create(client_admin=self.user1)
        self.property1 = PropertyFactory.create(client=self.client1)

    def test_that_string_representation_works(self):
        self.assertEqual(str(self.property1), self.property1.title)


class PropertyReviewTest(TestCase):
    """This class defines tests for property reviews"""

    def setUp(self):
        self.user1 = UserFactory.create()
        self.client1 = ClientFactory.create(client_admin=self.user1)
        self.property1 = PropertyFactory.create(client=self.client1)
        self.review1 = PropertyReviewFactory(
            reviewer=self.user1, target_property=self.property1)

    def test_that_string_representation_works(self):
        self.assertEqual(
            str(self.review1), f'Review by {self.user1} on {self.review1.created_at}')


class PropertyEnquiryTest(TestCase):
    """This class defines tests for property reviews"""

    def setUp(self):
        self.user1 = UserFactory.create()
        self.client1 = ClientFactory.create(client_admin=self.user1)
        self.property1 = PropertyFactory.create(client=self.client1)
        self.enquiry = PropertyEnquiryFactory(
            enquirer_name='Liz Kiherehere', target_property=self.property1)

    def test_that_string_representation_works(self):
        self.assertEqual(
            str(self.enquiry), f'Enquiry by Liz Kiherehere on {self.enquiry.created_at}')


class PropertyInspectionTest(TestCase):
    """This class defines tests for property inspections"""

    def setUp(self):
        self.user1 = UserFactory.create()
        self.client1 = ClientFactory.create(client_admin=self.user1)
        self.property1 = PropertyFactory.create(client=self.client1)
        self.inspection = PropertyInspectionFactory(
            requester=self.user1, target_property=self.property1)

    def test_that_string_representation_works(self):
        self.assertEqual(
            str(self.inspection), f'Inspection by {self.user1} due on {self.inspection.inspection_time}')
