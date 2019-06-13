from tempfile import NamedTemporaryFile
from rest_framework.exceptions import ValidationError

from tests.property import BaseTest
from property.validators import (
    validate_address, validate_coordinates, validate_image_list,
    get_file_extension, validate_image, validate_video)


class ValidatorTest(BaseTest):
    """Test that the property validators work as intended"""

    def test_that_city_cannot_be_empty(self):
        """Users must provide city information as strings that are not empty
        spaces"""

        with self.assertRaises(ValidationError) as e:
            validate_address(self.invalid_address_update)

        self.assertEqual(
            str(e.exception.detail[0]), 'City cannot be empty!')

    def test_that_address_must_contain_state(self):
        """Addresses that are submitted must contain City, Street and State
        information """
        update = self.invalid_address_update
        update["City"] = "Nairobi"
        update.pop('State')

        with self.assertRaises(ValidationError) as e:
            validate_address(update)
        self.assertEqual(
            str(e.exception.detail[0]),
            'Please provide a State name in your address.')

    def test_that_address_values_must_be_strings(self):
        """Address values should only be strings"""

        with self.assertRaises(ValidationError) as e:
            invalid_address = {"City": 3434.434,
                               "State": "Nairobi", "Street": "Wolf Street"}
            validate_address(invalid_address)

        self.assertEqual(str(e.exception.detail[0]),
                         "City should be letters.")

    def test_that_image_list_cannot_contain_floats(self):
        """There could be an edge case where users pass floats
        instead of valid urls"""

        with self.assertRaises(ValidationError) as e:
            validate_image_list([3454353.435])

        self.assertEqual(
            str(e.exception.detail[0]), "Please enter a valid url.")

    def test_that_coordinates_are_not_empty(self):
        """Coordinates should not have blank values"""

        invalid_coordinates = {"lon": "", "lat": 23454.45}
        with self.assertRaises(ValidationError) as e:
            validate_coordinates(invalid_coordinates)

        self.assertEqual(
            str(e.exception.detail.get('coordinates')),
            "lon cannot be empty!")

    def test_that_we_can_get_proper_file_extensions(self):

        ext = get_file_extension('image.jpeg')
        self.assertEqual(ext, 'jpeg')

        none = get_file_extension(443534)
        self.assertEqual(none, None)

    def test_that_images_cannot_exceed_10_MB(self):
        """Image files should not exceed 10MB"""

        img = NamedTemporaryFile(suffix='.jpg')
        img.size = 200000000
        with self.assertRaisesMessage(
                ValidationError,
                'Image files cannot be larger than 10.0 MBs.'):
            validate_image(img)
        img.close()

    def test_that_videos_cannot_exceed_50_MB(self):
        """Video files should not be larger than 50MB"""

        video = NamedTemporaryFile(suffix='.mp4')
        video.size = 800000000
        with self.assertRaisesMessage(
                ValidationError,
                'Video files cannot be larger than 50.0 MBs.'):
            validate_video(video)
        video.close()
