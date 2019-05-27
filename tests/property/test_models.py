from tests.property import BaseTest
from property.models import Property
from tests.factories.property_factory import (
    PropertyFactory, PropertyEnquiryFactory, PropertyReviewFactory,
    PropertyInspectionFactory
)
from tests.factories.authentication_factory import UserFactory, ClientFactory
from utils.slug_generator import generate_unique_slug as sluggify


class PropertyModelTest(BaseTest):
    """This class defines tests for the Property model"""

    def test_that_string_representation_works(self):
        self.assertEqual(str(self.property1), self.property1.title)

    def test_that_slugs_are_saved(self):

        address = {
            "City": "Cayman",
            "State": "Island",
            "Street": "Wall Street"
        }

        property_slug = PropertyFactory.create(
            client=self.client1, address=address)
        property_slug.save()
        expected_slug = f'wall-street-{property_slug.title.lower()}'
        self.assertEqual(expected_slug, property_slug.slug)


class PropertyReviewTest(BaseTest):
    """This class defines tests for property reviews"""

    def test_that_string_representation_works(self):
        self.assertEqual(
            str(self.review1), f'Review by {self.user1} on {self.review1.created_at}')


class PropertyEnquiryTest(BaseTest):
    """This class defines tests for property reviews"""

    def test_that_string_representation_works(self):
        self.assertEqual(
            str(self.enquiry1), f'Enquiry by Liz Kiherehere on {self.enquiry1.created_at}')


class PropertyInspectionTest(BaseTest):
    """This class defines tests for property inspections"""

    def test_that_string_representation_works(self):
        self.assertEqual(
            str(self.inspection1), f'Inspection by {self.user1} due on {self.inspection1.inspection_time}')
