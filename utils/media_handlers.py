import logging

from django.utils.datastructures import MultiValueDictKeyError
from django.conf import settings
import cloudinary.uploader as uploader
from cloudinary.api import delete_resources, Error
from rest_framework.exceptions import ValidationError

from property.validators import (
    validate_cloudinary_url, validate_image, validate_video)
from property.models import MAX_PROPERTY_IMAGE_COUNT


if not settings.DEBUG:
    logger = logging.getLogger('productionLogger')
else:
    logger = logging.getLogger('testLogger')


class CloudinaryResourceHandler:
    """This class contains methods for handling Cloudinary
    Resources, ie images and vidoes."""

    def upload_image(self, image):
        """Upload an image to cloudinary and return the url.
        The image should be an instance of Django's UploadedFile
        class. Read more about the UploadedFile class here
        https://docs.djangoproject.com/en/2.2/ref/files/uploads/#django.core.files.uploadedfile.UploadedFile
        Image file is first validated before being uploaded.
        """
        try:
            logger.debug('Validating image before uploading...')
            validate_image(image)
            logger.debug('Uploading image to Cloudinary')
            result = uploader.upload(image)
            url = result.get('url')
            logger.info(
                'Successfully uploaded image to Cloudinary. Returned url: '
                f'{url}')
            return url
        # Cloudinary might still throw an error if validation fails.
        except Error as e:
            logger.warning('Upload to cloudinary failed. Error raised: '
                           f'{e}')
            raise ValidationError({
                'image':
                ('Image is either corrupted or of an unkown format. '
                    'Please try again with a different image file.')
            }) from e

    def upload_image_from_request(self, request):
        """Upload an image directly from a request object.
        params:
            request - incoming request object
        Return:
            the url if upload is successful.
        """
        try:
            image_main = request.FILES['image_main']

            if image_main:
                url = self.upload_image(image_main)
                return url

        except MultiValueDictKeyError:
            # This error will be raised if `image_main` is not an
            # uploaded file. There is no need to raise an error in that
            # case
            logger.debug('No main image was passed in the request.')
            pass

    def upload_image_batch(self, request, instance=None):
        """Upload multiple images from a request object.
        params:
            request - incoming request object
            instance - optional. Only pass when updating images.
                This is the instance to be updated.
                We use this to ensure that the instance does
                not have more than 15 images after update is
                finished.
        Return:
            list containing urls of uploaded images
        """

        image_list = request.FILES.getlist('image_others')
        # this is the error message returned when users will exceed their
        # limit whenever creating or updating property images.
        if image_list:
            logger.debug(
                f'{len(image_list)} images found in the key `image_others`')
            max_image_count_exceeded = (
                'Sorry. You are limited to a maximum '
                f'of {MAX_PROPERTY_IMAGE_COUNT} images. '
                'Please reduce the number '
                'of images you '
                'wish to upload and try again.')
            if len(image_list) > MAX_PROPERTY_IMAGE_COUNT:
                logger.debug('Max image limit exceeded.')
                raise ValidationError({
                    'image_others': max_image_count_exceeded}
                )
            elif image_list and (instance is not None):
                image_count_in_DB = len(instance.image_others)
                # check to ensure that updating the images will not result
                # in more than 15 images being saved for this instance.
                if image_count_in_DB + len(image_list) > (
                        MAX_PROPERTY_IMAGE_COUNT):
                    logger.info('Max image limit exceeded.')
                    raise ValidationError({
                        'image_others': max_image_count_exceeded}
                    )
            return [self.upload_image(image) for image in image_list]
        # if there are no images to be updated, we return an empty list
        # instead of None. The field `image_others` should not contain
        # null values.
        logger.debug('No images to be uploaded under key `image_others`')
        return []

    def upload_video(self, video):
        """Upload a video file to Cloudinary.
        First validate that the video file is of supported size
        and format before uploading.
        params:
            video - Video file to be uploaded
        Return:
            Cloudinary video url if upload is successful
        """
        try:
            logger.debug('Validating video before uploading to Cloudinary...')
            validate_video(video)
            logger.debug(
                'Valid video found. Attempting to upload to Cloudinary.')
            res = uploader.upload_large(
                video, resource_type="video")
            url = res.get('url')
            logger.info(f'Video upload succesful. Returned url: {url}')
            return url
        except Error as e:
            # Cloudinary might throw an error during upload
            logger.error(f'Video upload failed. Error raised: {e}')
            raise ValidationError({
                'video': ('Video is either corrupted or of an unkown format.'
                          'Please try again with a different video file.')
            }) from e

    def upload_video_from_request(self, request):
        """Upload a video direclty from a request object.
        If users submit a video link, we return that link to be
        saved to the database.
        If they submit a video file, we upload the file to Cloudinary
        and return the url to be saved to the database."""

        video_file = request.FILES.getlist('video')
        video_link = request.data.get('video')
        if video_file:
            # We only allow users to upload maximum of one video
            url = self.upload_video(video_file[0])
            return url
        elif video_link:
            logger.debug('Video link passed instead of video file.')
            return video_link

    def get_cloudinary_public_id(self, url):
        """Get the `public_id` of a Cloudinary resource from the url.
        params:
            url - Url of the resource
        returns:
            public_id of the cloudinary resource if the url is valid
            Raise Validation error if it is not a Cloudinary url
        """
        # validate that the url is a valid cloudinary url first. If it is not
        # then a ValidationError is raised. You should handle this exception
        # and implement logic to fit your needs if the url isn't Cloudinary's

        validate_cloudinary_url(url)
        file_name = url.split('/')[-1]
        public_id = file_name.split('.')[0]
        return public_id

    def delete_cloudinary_resource(self, instance, payload):
        """Delete a Cloudinary resource.
        params:
            instance - instance of the model from which to delete the resource.
            payload - dictionary where the key is the field to find the
                      resource and the value is the url to delete from field.

        We check the field to confirm that the value is stored there and
        proceed to delete it from the database and also from Cloudinary.

        Return:
            updated_fields - Dictionary containting the updated values of
                             our model. Should be passed to the serailizer
                             for updating.

        """
        # we need to ensure that the payload is an instance of a dictionary
        # and can be converted to one before we proceed.

        updated_fields = {}

        deleted_image_others = payload.get('image_others')
        deleted_video = payload.get('video')

        image_list_in_DB = instance.image_others.copy() if instance.image_others else []  # noqa
        video_in_DB = instance.video
        if deleted_image_others:
            logger.debug(
                f'{len(deleted_image_others)} images to be deleted...')
            for image in deleted_image_others:
                if image in image_list_in_DB:
                    try:
                        logger.debug(
                            'Checking if resource has a Cloudinary public id')
                        public_image_id = self.get_cloudinary_public_id(image)
                        logger.debug(
                            'Attempting to delete image with public id '
                            f'{public_image_id} from Cloudinary...')
                        uploader.destroy(public_image_id, invalidate=True)
                        instance.image_others.remove(image)
                        logger.debug('Deleted the image from database.')
                    except ValidationError:
                        # if the image is not from cloudinary, we simply delete
                        # it from the DB
                        logger.info('Image is not from Cloudinary. Attempting '
                                    'to remove it from the DB...')
                        instance.image_others.remove(image)

            logger.info('Images deleted from the database.'
                        f'{len(instance.image_others)} images '
                        'left for this property')
            updated_fields['image_others'] = instance.image_others

        if video_in_DB == deleted_video:

            try:
                # because video urls don't have to be cloudinary urls,
                # we first try and check if it's a cloudinary resource
                # before deleting it.
                logger.debug('Checking is video has public Cloudinary id...')
                public_video_id = self.get_cloudinary_public_id(deleted_video)
                logger.debug('Attempting to delete video with public id '
                             f'{public_video_id} from Cloudinary...')
                delete_resources(
                    public_video_id, resource_type='video', invalidate=True)
            except ValidationError:
                # if the video in the DB is not a cloudinary url, we just pass
                # but still delete it from the DB in the `finally`
                # statement below
                logger.debug('Video to be deleted is not from Cloudinary.')
                pass

            finally:
                # as long as the video link in the request matches that in
                # the database we delete that video from the database.
                logger.debug('Deleting the video from the database.')
                instance.video = None
            logger.info('Video deleted from the database. Boolean value for '
                        f'the property video is {bool(instance.video)}. '
                        'It should be False.')
            updated_fields['video'] = None

        instance.save()
        return updated_fields
