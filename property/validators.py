from django.core.validators import URLValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError


def validate_address(address):
    if not isinstance(address, dict):
        raise ValidationError(
            "Address should be a dictionary with city, state and street information.")
    KEYS = ["City", "State", "Street"]
    for key in KEYS:
        if key not in address.keys():
            raise ValidationError(
                f"Please provide a {key} name in your address.")
    for key, value in address.items():
        if not isinstance(value, str):
            raise ValidationError(f"{key} should be letters.")
        if not value.strip():
            raise ValidationError(f"{key} cannot be empty!")


def validate_image_list(image_list):
    for image in image_list:
        validator = URLValidator()
        try:
            validator(image)
        except DjangoValidationError:
            raise ValidationError("Please enter valid urls for your images.")
        except AttributeError:
            raise ValidationError("Please enter valid urls for your images.")


def validate_coordinates(coordinates):
    if not isinstance(coordinates, dict):
        raise ValidationError(
            "Please ensure your coordinates are submitted as a valid dictionary.")
    for key, value in coordinates.items():
        # we stringigy the value so that we can check if it is empty
        value = str(value)
        if not value.strip():
            raise ValidationError(
                {"coordinates": f"{key} cannot be empty!"})
