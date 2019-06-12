from rest_framework.serializers import ValidationError

from tests.property import BaseTest
from property.serializers import PropertySerializer
from property.models import Property
from tests.factories.authentication_factory import UserFactory, ClientFactory


class PropertySerializerTest(BaseTest):
    """This class contains unit tests for Property Serializer"""

    def test_serializer_class_works_properly(self):
        serializer = PropertySerializer(data=self.property_data)
        self.assertTrue(serializer.is_valid())
        new_property = serializer.save()
        self.assertIsInstance(new_property, Property)

    def test_serialiser_throws_an_error_if_address_is_not_dictionary(self):
        """Address should be a valid dictionary for it to be saved in the database"""

        data = self.property_data
        data['address'] = "this should be a dictionary, not a string!"

        serializer = PropertySerializer(data=data)
        with self.assertRaises(ValidationError) as e:
            serializer.is_valid(raise_exception=True)

        self.assertEqual(str(e.exception.detail.get('address')[
                         0]), 'Address should be a dictionary with city, state and street information.')

    def test_serializer_returns_error_if_city_information_is_not_in_the_address(self):
        """Users should provide City name when they provide us with the address of their property"""

        data = self.property_data
        data['address'] = {"Street": "Wolf Street", "State": "Washington"}

        serializer = PropertySerializer(data=data)
        with self.assertRaises(ValidationError) as e:
            serializer.is_valid(raise_exception=True)

        self.assertEqual(str(e.exception.detail.get('address')[
                         0]), 'Please provide a City name in your address.')

    def test_serializer_returns_error_if_street_information_is_not_in_the_address(self):
        """Users should provide Street name when they provide us with the address of their property"""

        data = self.property_data
        data['address'] = {"City": "Seattle", "State": "State"}

        serializer = PropertySerializer(data=data)
        with self.assertRaises(ValidationError) as e:
            serializer.is_valid(raise_exception=True)

        self.assertEqual(str(e.exception.detail.get('address')[
                         0]), 'Please provide a Street name in your address.')

    def test_serializer_returns_error_if_state_information_is_not_in_the_address(self):
        """Users should provide State name when they provide us with the address of their property"""

        data = self.property_data
        data['address'] = {"City": "Seattle", "Street": "Wolf Street"}

        serializer = PropertySerializer(data=data)
        with self.assertRaises(ValidationError) as e:
            serializer.is_valid(raise_exception=True)

        self.assertEqual(str(e.exception.detail.get('address')[
                         0]), 'Please provide a State name in your address.')

    def test_serialiser_throws_an_error_if_coordinates_is_not_dictionary(self):
        """Coordinates should be a valid dictionary for it to be saved in the database"""

        data = self.property_data
        data['coordinates'] = "this should be a dictionary, not a string!"

        serializer = PropertySerializer(data=data)
        with self.assertRaises(ValidationError) as e:
            serializer.is_valid(raise_exception=True)

        self.assertEqual(str(e.exception.detail.get('coordinates')[
                         0]), 'Please ensure your coordinates are submitted as a valid dictionary.')

    def test_that_image_list_must_contain_valid_urls(self):
        """Property image lists should only contain valid urls"""

        data = self.property_data
        data['image_others'] = [
            "http://www.example.com", "enter valid url please"]

        serializer = PropertySerializer(data=data)
        with self.assertRaises(ValidationError) as e:
            serializer.is_valid(raise_exception=True)

        self.assertEqual(str(e.exception.detail.get('image_others')[
                         0]), 'Please enter valid urls for your images.')
