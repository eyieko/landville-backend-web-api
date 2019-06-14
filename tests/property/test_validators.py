from rest_framework.exceptions import ValidationError

from tests.property import BaseTest
from property.validators import validate_address, validate_coordinates, validate_image_list


class ValidatorTest(BaseTest):
    """Test that the property validators work as intended"""

    def test_that_city_cannot_be_empty(self):
        """Users must provide city information as strings that are not empty spaces"""

        with self.assertRaises(ValidationError) as e:
            validate_address(self.invalid_address_update)

        self.assertEqual(
            str(e.exception.detail[0]), 'Please provide a City name in your address.')

    def test_that_address_values_must_be_strings(self):
        """Address values should only be strings"""

        with self.assertRaises(ValidationError) as e:
            invalid_address = {"City": 3434.434,
                               "State": "Nairobi", "Street": "Wolf Street"}
            validate_address(invalid_address)

        self.assertEqual(str(e.exception.detail[0]), "City should be letters.")

    def test_that_image_list_cannot_contain_floats(self):
        """There could be an edge case where users pass floats instead of valid urls"""

        with self.assertRaises(ValidationError) as e:
            validate_image_list([3454353.435])

        self.assertEqual(
            str(e.exception.detail[0]), "Please enter valid urls for your images.")

    def test_that_coordinates_are_not_empty(self):
        """Coordinates should not have blank values"""

        invalid_coordinates = {"lon": "", "lat": 23454.45}
        with self.assertRaises(ValidationError) as e:
            validate_coordinates(invalid_coordinates)

        self.assertEqual(
            str(e.exception.detail.get('coordinates')), "lon cannot be empty!")
