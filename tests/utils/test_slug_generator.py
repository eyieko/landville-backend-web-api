from django.test import TestCase

from utils.slug_generator import generate_unique_slug as sluggify
from tests.factories.property_factory import PropertyFactory


class TestSlugGenerator(TestCase):
    """This class contains unit tests for the slug generator"""

    def test_slug_generator_creates_slug_when_no_street_is_present(self):
        """When the property instance passed doesn't have street data,
        the slug should only contain title and incrementing integer"""

        address = {"City": "Nairobi"}

        property_instance = PropertyFactory.create(
            title="dummy", address=address)
        slug = sluggify(property_instance, 'slug')
        self.assertEqual(slug, 'dummy-1')
