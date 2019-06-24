from django.core.validators import URLValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.conf import settings
from rest_framework.exceptions import ValidationError


def validate_address(address):
    if not isinstance(address, dict):
        raise ValidationError(
            "Address should contain City, State and Street.")
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


def validate_url(url):
    """
    Validate that the url passed is valid. Takes a string and returns
    True if the string is a valid url.
    """
    validator = URLValidator()
    try:
        validator(url)
        return True
    except (DjangoValidationError, AttributeError) as e:
        raise ValidationError("Please enter a valid url.") from e


def validate_image_list(image_list):
    for image in image_list:
        validate_url(image)


def validate_cloudinary_url(url):
    """Validate that the url is a valid cloudinary url."""
    try:
        validate_url(url)
        assert (f'cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}' in url)
    except (AssertionError, ValidationError) as e:
        raise ValidationError("Not a valid cloudinary url.") from e


def validate_coordinates(coordinates):
    if not isinstance(coordinates, dict):
        raise ValidationError(
            "Coordinates should be a valid dictionary.")
    for key, value in coordinates.items():
        # we stringigy the value so that we can check if it is empty
        value = str(value)
        if not value.strip():
            raise ValidationError(
                {"coordinates": f"{key} cannot be empty!"})


def get_file_extension(file_name):
    """Return the file extension of a file given the filename.
    The filename should be a string with the file extension.
    Return: None if the file_name is not a string
    Return: extension if the file_name has an extension. Note
    that the extension is expected to be the string after the last
    `.` in the file_name."""
    if not isinstance(file_name, str):
        return None
    extension = file_name.split('.')[-1]
    return extension


def validate_image(image):
    """Check the image extension and size to ensure it is a valid type
    before uploading to Cloudinary. The image should be a django UploadedFile
    instance.
    https://docs.djangoproject.com/en/2.2/ref/files/uploads/#django.core.files.uploadedfile.UploadedFile
    """

    VALID_EXTENSIONS = ['jpg', 'png', 'jpeg']
    IMAGE_SIZE = 10000000  # 10MB
    extension = get_file_extension(image.name)

    if extension not in VALID_EXTENSIONS:
        raise ValidationError({
            'image': f'Please provide a valid image format.'
        })
    if image.size > IMAGE_SIZE:
        raise ValidationError({
            'image':
            f'Image files cannot be larger than {IMAGE_SIZE/1000000} MBs.'
        })


def validate_video(video):
    """Check the image extension and size to ensure it is valid before
    uploading to Cloudinary. The video should be an instance of Django's
    UploadedFile class. """

    VALID_EXTENSIONS = ['mp4', 'flv']
    VIDEO_SIZE = 50000000  # 50MB
    extension = get_file_extension(video.name)
    if extension not in VALID_EXTENSIONS:
        raise ValidationError({
            'video': f'Please provide a valid video file format.'
        })
    if video.size > VIDEO_SIZE:
        raise ValidationError({
            'video':
            f'Video files cannot be larger than {VIDEO_SIZE/1000000} MBs.'
        })
