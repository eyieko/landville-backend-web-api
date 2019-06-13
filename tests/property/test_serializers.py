from rest_framework.serializers import ValidationError

from tests.property import BaseTest
from property.serializers import PropertySerializer
from property.models import Property


class PropertySerializerTest(BaseTest):
    """This class contains unit tests for Property Serializer"""

    def test_serializer_class_works_properly(self):
        data = {
            "title": self.property2.title,
            "address": self.property2.address,
            "coordinates": self.property2.coordinates,
            "client": self.client1.pk,
            "description": "Description",
            "price": self.property2.price,
            "lot_size": self.property2.lot_size,
            "image_main": self.property2.image_main,
            "purchase_plan": self.property2.purchase_plan
        }
        serializer = PropertySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        new_property = serializer.save()
        self.assertIsInstance(new_property, Property)

    def test_serialiser_throws_an_error_if_address_is_not_dictionary(self):
        """Address should be a valid dictionary for it to be saved"""

        data = self.property_data
        data['address'] = "this should be a dictionary, not a string!"

        serializer = PropertySerializer(data=data)
        with self.assertRaises(ValidationError) as e:
            serializer.is_valid(raise_exception=True)

        self.assertEqual(
            str(e.exception.detail.get('address')[0]),
            'Address should contain City, State and Street.')

    def test_serializer_returns_error_if_city_is_not_in_the_address(self):
        """Users should provide City name when they provide us with
        the address of their property"""

        data = self.property_data
        data['address'] = {"Street": "Wolf Street", "State": "Washington"}

        serializer = PropertySerializer(data=data)
        with self.assertRaises(ValidationError) as e:
            serializer.is_valid(raise_exception=True)

        self.assertEqual(str(e.exception.detail.get('address')[
                         0]), 'Please provide a City name in your address.')

    def test_serializer_returns_error_if_street_is_not_in_the_address(self):
        """Users should provide Street name when they provide us
        with the address of their property"""

        data = self.property_data
        data['address'] = {"City": "Seattle", "State": "State"}

        serializer = PropertySerializer(data=data)
        with self.assertRaises(ValidationError) as e:
            serializer.is_valid(raise_exception=True)

        self.assertEqual(str(e.exception.detail.get(
            'address')[0]), 'Please provide a Street name in your address.')

    def test_serializer_returns_error_if_state_is_not_in_the_address(self):
        """Users should provide State name when they provide us with
        the address of their property"""

        data = self.property_data
        data['address'] = {"City": "Seattle", "Street": "Wolf Street"}

        serializer = PropertySerializer(data=data)
        with self.assertRaises(ValidationError) as e:
            serializer.is_valid(raise_exception=True)

        self.assertEqual(str(e.exception.detail.get(
            'address')[0]), 'Please provide a State name in your address.')

    def test_serialiser_throws_error_if_coordinates_is_not_dictionary(self):
        """Coordinates should be a valid dictionary for it to be saved"""

        data = self.property_data
        data['coordinates'] = "this should be a dictionary, not a string!"

        serializer = PropertySerializer(data=data)
        with self.assertRaises(ValidationError) as e:
            serializer.is_valid(raise_exception=True)

        self.assertEqual(
            str(e.exception.detail.get('coordinates')[0]),
            'Coordinates should be a valid dictionary.')

    def test_that_image_list_must_contain_valid_urls(self):
        """Property image lists should only contain valid urls"""

        data = self.property_data
        data['image_others'] = [
            "http://www.example.com", "enter valid url please"]

        serializer = PropertySerializer(data=data)
        with self.assertRaises(ValidationError) as e:
            serializer.is_valid(raise_exception=True)

        self.assertEqual(str(e.exception.detail.get('image_others')[
                         0]), 'Please enter a valid url.')

    def test_that_the_serializer_update_method_handles_resource_updates(self):
        """Updating images and videos is mainly done in the serialize.
        Test ensures that the data is properly serialized and the relevant
        models are updated """

        data = self.property_update
        data['client'] = self.property_no_images.client.pk
        data['image_others'] = [
            "http://www.example.com", "http://www.uploaded.properly/"]
        data['address'] = '{"City": "Nam", "State": "Nim", "Street": "Nom" }'
        data['coordinates'] = '{ "lon": 843535, "lan": 344534}'
        # Because the Django's QueryDict will have all values in a list, we
        # simulate this condition when passing the video url, although in
        # actual sense, the url will just be a string.
        data['video'] = ["http://www.videos.com"]
        serializer = PropertySerializer(
            self.property_no_images, data=data, partial=True)
        serializer.is_valid()
        data['client'] = self.property_no_images.client
        serializer.update(self.property_no_images, data)
        self.assertEqual(len(self.property_no_images.image_others), 2)
        self.assertEqual(self.property_no_images.video,
                         'http://www.videos.com')
