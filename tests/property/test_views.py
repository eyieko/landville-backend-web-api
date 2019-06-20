from tempfile import NamedTemporaryFile
from unittest.mock import patch, Mock
import json

from django.urls import reverse
from django.test.client import encode_multipart
from rest_framework import status
from rest_framework.test import force_authenticate
from cloudinary.api import Error

from tests.property import BaseTest
from tests.factories.authentication_factory import UserFactory
from property.views import (CreateAndListPropertyView,
                            PropertyDetailView,
                            BuyerPropertyListView,
                            TrendingPropertyView,
                            ListCreateEnquiryAPIView,
                            PropertyEnquiryDetailView
                            )
from property.models import Property, MAX_PROPERTY_IMAGE_COUNT
from tests.factories.property_factory import PropertyFactory


def get_one_enquiry(enquiry_id):
    return reverse("property:one-enquiry", args=[enquiry_id])


GET_ALL_ENQURIES_URL = reverse('property:all-enquiries')


def post_enquiry_url(property_slug):
    return reverse("property:post_enquiry", args=[property_slug])


class PropertyViewTests(BaseTest):
    """This class defines tests for the different property views"""

    @patch('utils.media_handlers.uploader.upload')
    @patch('utils.media_handlers.uploader.upload_large')
    def test_that_client_admins_can_create_property(
            self, mock_upload, mock_video_upload):
        """Admin Clients should be able to create property if
        they provide correct information """

        temp_main_image = NamedTemporaryFile(suffix='.jpeg')
        temp_image1 = NamedTemporaryFile(suffix='.jpg')
        temp_image2 = NamedTemporaryFile(suffix='.png')
        temp_video1 = NamedTemporaryFile(suffix='.mp4')

        mock_upload.return_value = {'url': 'http://www.upload.com/'}
        mock_video_upload.return_value = {
            'url': 'http://www.video.com/uploaded'}

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.user1.token}')

        data = self.property_data
        data['image_main'] = temp_main_image
        data['image_others'] = [temp_image1, temp_image2]
        data['video'] = temp_video1

        content = encode_multipart('BoUnDaRyStRiNg', data)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        res = self.client.post(self.create_list_url,
                               content, content_type=content_type)
        temp_main_image.close()
        temp_image1.close()
        temp_image2.close()
        temp_video1.close()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    @patch('utils.media_handlers.uploader.upload')
    def test_that_client_admins_can_create_property_with_video_links(
            self, mock_upload):
        """Admin Clients should be able to create property if
        they provide correct information.
        The video can be a link instead of a file."""

        temp_main_image = NamedTemporaryFile(suffix='.jpeg')
        temp_image1 = NamedTemporaryFile(suffix='.jpg')
        temp_image2 = NamedTemporaryFile(suffix='.png')

        mock_upload.return_value = {'url': 'http://www.upload.com/'}

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.user1.token}')

        data = self.property_data
        data['image_main'] = temp_main_image
        data['image_others'] = [temp_image1, temp_image2]
        # we pass a url for the video instead of a file
        data['video'] = 'http://www.video/com/upload/please'

        content = encode_multipart('BoUnDaRyStRiNg', data)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        res = self.client.post(self.create_list_url,
                               content, content_type=content_type)
        temp_main_image.close()
        temp_image1.close()
        temp_image2.close()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            res.data.get('data')['property']['video'],
            'http://www.video/com/upload/please')

    @patch('utils.media_handlers.uploader.upload')
    def test_that_valid_image_file_formats_must_be_passed(self, mock_upload):
        """Client admins should only pass images with valid file formats."""

        temp_main_image = NamedTemporaryFile(suffix='.pdf')

        mock_upload.return_value = {'url': 'http://www.upload.com/'}

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.user1.token}')

        data = self.property_data
        data['image_main'] = temp_main_image

        content = encode_multipart('BoUnDaRyStRiNg', data)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        res = self.client.post(self.create_list_url,
                               content, content_type=content_type)
        temp_main_image.close()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(res.data['errors'].get(
            'image')), 'Please provide a valid image format.')

    @patch('utils.media_handlers.uploader.upload')
    @patch('utils.media_handlers.uploader.upload_large')
    def test_that_valid_video_file_formats_must_be_passed(
            self, mock_upload, mock_video_upload):
        """Client admins should only pass videos with valid file formats."""

        temp_main_image = NamedTemporaryFile(suffix='.jpg')
        temp_video = NamedTemporaryFile(suffix='.mkv')

        mock_upload.return_value = {'url': 'http://www.upload.com/'}
        mock_video_upload.return_value = {
            'url': 'http://www.video.uploaded/plus/'}

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.user1.token}')

        data = self.property_data
        data['image_main'] = temp_main_image
        data['video'] = temp_video

        content = encode_multipart('BoUnDaRyStRiNg', data)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        res = self.client.post(self.create_list_url,
                               content, content_type=content_type)
        temp_main_image.close()
        temp_video.close()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(
            res.data['errors'].get('video')),
            'Please provide a valid video file format.')

    def test_that_users_who_are_not_client_admins_cannot_create_property(
            self):
        """Only client admins should be able to create property"""

        self.user1.role = 'BY'

        request = self.factory.post(
            self.create_list_url, self.property_data, format='json')
        force_authenticate(request, user=self.user1)
        view = CreateAndListPropertyView.as_view()
        response = view(request, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_that_users_who_are_not_logged_in_cannot_create_property(self):
        """Only client admins should be able to create property"""

        request = self.factory.post(
            self.create_list_url, self.property_data, format='json')
        view = CreateAndListPropertyView.as_view()
        response = view(request, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_that_client_admins_can_view_all_their_undeleted_property(self):
        """
        Client admins should see all their property that is not deleted,
        regardless of whether the property is published or not
        """

        request = self.factory.get(
            self.create_list_url)
        force_authenticate(request, user=self.user1)
        view = CreateAndListPropertyView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results')), 5)
        self.assertTrue(response.data.get('results')[0].get(
            'is_published') and response.data.get('results')[2].get(
                'is_published'))

    def test_that_buyers_can_see_only_published_property_that_are_not_deleted(
            self):
        """Buyers should only be able to see property that is published
        and not deleted"""
        buyer = UserFactory.create()

        request = self.factory.get(
            self.create_list_url)
        force_authenticate(request, user=buyer)
        view = CreateAndListPropertyView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # only one property is published and not deleted
        self.assertEqual(len(response.data.get('results')), 4)
        self.assertEqual(response.data.get('results')[2].get(
            'title'), 'HardCoded Title Block')

    def test_that_admins_can_view_all_property(self):
        """Admins should be able to see all property regardless of whether
         it is published or soft deleted"""

        request = self.factory.get(
            self.create_list_url)
        self.user1.role = 'LA'
        self.user1.save()
        force_authenticate(request, user=self.user1)
        view = CreateAndListPropertyView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        all_property = Property.objects.all().count()
        # admins view all property in the database
        self.assertEqual(len(response.data.get('results')), all_property)

    def test_that_only_client_admins_can_create_property(self):
        """Only client admins who currently have client companies can create
        property"""

        non_client_admin = UserFactory.create()

        post_request = self.factory.post(
            self.create_list_url, self.property_data, format='json')
        force_authenticate(post_request, user=non_client_admin)
        view = CreateAndListPropertyView.as_view()
        response = view(post_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_client_admins_can_view__unpublished_property_that_they_own(self):
        """Client admins should be able to view a specific property
        they own regardless of whether it is published or not.
        They cannot view property that is deleted, however
        """

        # self.property1 is not published
        url = reverse('property:single_property', args=[self.property11.slug])
        request = self.factory.get(url)
        force_authenticate(request, user=self.user1)
        view = PropertyDetailView.as_view()
        response = view(request, slug=self.property11.slug)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data.get('is_published'))

    def test_that_client_admins_can_update_their_property(self):
        """Client admins should be able to update their property"""

        url = reverse('property:single_property', args=[self.property11.slug])

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.user1.token}')
        update_data = self.property_update
        update_data.pop('image_others')
        update_data['address'] = json.dumps({
            "City": "TestVille", "State": "StateVille", "Street": "Street"
        })
        update_data['coordinates'] = json.dumps({
            "lan": 353454, "lon": 345345
        })
        content = encode_multipart('BoUnDaRyStRiNg', update_data)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        response = self.client.patch(
            url, content, content_type=content_type
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('data')['property']['price'], 99999999.99)
        self.assertEqual(
            response.data.get('data')['property']['title'],
            'Updated Super Lot')

    def test_client_admin_cannot_view_property_that_is_not_published(self):
        """A client admin should not be able to view property belonging to
        different clients if the property is not published"""

        url = reverse('property:single_property', args=[self.property11.slug])

        request = self.factory.get(url)
        force_authenticate(request, user=self.user2)
        view = PropertyDetailView.as_view()
        response = view(request, slug=self.property11.slug)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_client_admins_cannot_update_property_belonging_to_other_clients(
            self):
        """Client admins shouldn't be able to update property belonging to
        different companies"""

        view = PropertyDetailView.as_view()

        url = reverse('property:single_property', args=[self.property2.slug])
        content = encode_multipart('BoUnDaRyStRiNg', self.property_update)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        request = self.factory.patch(url, content, content_type=content_type)

        response2 = view(
            request, slug=self.property2.slug, format='json'
        )
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)

        # if they try to view the published property, they surely can
        get_request = self.factory.get(url)
        force_authenticate(get_request, user=self.user2)
        response3 = view(
            get_request, slug=self.property2.slug
        )
        self.assertEqual(response3.status_code, status.HTTP_200_OK)

    def test_that_landville_staff_can_view_all_property(self):
        """
        LandVille staff should be able to view all
        property regardless of any parameters
        """

        view = PropertyDetailView.as_view()

        url = reverse('property:single_property', args=[self.property1.slug])
        request = self.factory.get(url)
        force_authenticate(request, user=self.admin)
        response = view(request, slug=self.property1.slug)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_that_client_admin_can_delete_their_property(self):
        """Client admins should be able to delete their property"""

        view = PropertyDetailView.as_view()

        url = reverse('property:single_property', args=[self.property11.slug])
        request = self.factory.delete(url)
        force_authenticate(request, user=self.user1)
        response = view(request, slug=self.property11.slug)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_client_admins_should_have_client_before_they_can_create_property(
            self):
        """Client admins should have the role `CA` and they should also have
        an employer before they can create property """

        post_request = self.factory.post(
            self.create_list_url, self.property_data, format='json')

        # this user has role `CA` but has no employer relationship
        fake_client = UserFactory.create()
        fake_client.role = 'CA'
        fake_client.save()
        force_authenticate(post_request, user=fake_client)
        view = CreateAndListPropertyView.as_view()
        response = view(post_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_that_landville_staff_can_update_property(self):
        """LandVille staff should be able to update a property"""

        url = reverse('property:single_property', args=[self.property11.slug])

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.admin.token}')
        update_data = self.property_update
        update_data.pop('image_others')
        content = encode_multipart('BoUnDaRyStRiNg', update_data)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        response = self.client.patch(
            url, content, content_type=content_type
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('data')['property']['price'], 99999999.99)
        self.assertEqual(
            response.data.get('data')['property']['title'],
            'Updated Super Lot')

    def test_landville_staff_cannot_delete_property_that_is_already_deleted(
            self):
        """Because LandVille staff can view property that is already deleted,
        they should not be able to delete that property again. """

        view = PropertyDetailView.as_view()

        # property1 is already soft deleted
        url = reverse('property:single_property', args=[self.property1.slug])
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin)
        response = view(request, slug=self.property1.slug)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('errors'),
                         'Not allowed! This property is already deleted.')

    def test_users_should_pass_valid_address_values(self):
        """Users should not be able to send invalid addresses like numbers
        and empty strings """
        url = reverse('property:single_property', args=[self.property11.slug])

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.user1.token}')
        update_data = self.property_update
        update_data['address'] = json.dumps(self.invalid_address_update)
        update_data.pop('image_others')
        content = encode_multipart('BoUnDaRyStRiNg', update_data)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        response = self.client.patch(
            url, content, content_type=content_type
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['errors'].get('address')[
            0]), 'City cannot be empty!')

    @patch('utils.media_handlers.uploader.upload')
    def test_that_users_have_a_choice_to_update_many_images_or_not(
            self, mock_upload):
        """Client admins can update one image or many, as they see fit"""

        mock_upload.return_value = {'url': 'http://www.uploaded.com/'}
        expected_image_others = [
            'http://www.uploaded.com/', 'http://www.uploaded.com/']

        url = reverse('property:single_property', args=[
                      self.property_no_images.slug])

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.user2.token}')
        update_data = self.property_update
        temp_image1, temp_image2 = [
            NamedTemporaryFile(suffix='.png'),
            NamedTemporaryFile(suffix='.jpg')]
        update_data['image_others'] = [temp_image1, temp_image2]
        update_data['main_image'] = temp_image1
        update_data['is_published'] = True
        content = encode_multipart('BoUnDaRyStRiNg', update_data)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'

        response = self.client.patch(
            url, content, content_type=content_type
        )
        temp_image1.close()
        temp_image2.close()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('data')['property']['price'], 99999999.99)
        self.assertEqual(
            response.data.get('data')['property']['image_others'],
            expected_image_others)
        # assert that `is_published` is not updated
        self.assertFalse(response.data.get('data')['property']['is_published']
                         )

    @patch('utils.media_handlers.delete_resources')
    def test_that_client_admins_can_delete_images_and_video_for_property(
            self, mock_delete):
        """Client admins should be able to delete images and video for
        their property"""

        dummy_property = PropertyFactory.create(
            image_others=[self.cloudinary_image_url1,
                          self.cloudinary_image_url2],
            video=self.cloudinary_video_url1,
            client=self.client1)

        url = reverse('property:delete_cloudinary_resource', args=[
                      dummy_property.slug])

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.user1.token}')
        update_data = {'image_others': [dummy_property.image_others[0]],
                       'video': dummy_property.video}
        response = self.client.delete(
            url, update_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('data')[
                         'property']['image_others']), 1)
        self.assertEqual(response.data.get('data')['property'][
                         'image_others'][0], self.cloudinary_image_url2)
        self.assertEqual(response.data.get('data')['property']['video'], None)

    @patch('utils.media_handlers.delete_resources')
    def test_that_landville_staff_can_delete_images_and_video_for_property(
            self, mock_delete):
        """LandVille staff should be able to delete images and video for
        listed property"""

        dummy_property = PropertyFactory.create(
            image_others=[self.cloudinary_image_url1,
                          self.cloudinary_image_url2],
            video=self.cloudinary_video_url1,
            client=self.client1)

        url = reverse('property:delete_cloudinary_resource', args=[
                      dummy_property.slug])

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.admin.token}')
        update_data = {'image_others': [dummy_property.image_others[0]],
                       'video': dummy_property.video}
        response = self.client.delete(
            url, update_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('data')[
                         'property']['image_others']), 1)
        self.assertEqual(response.data.get('data')['property'][
                         'image_others'][0], self.cloudinary_image_url2)
        self.assertEqual(response.data.get('data')['property']['video'], None)

    def test_that_client_admins_can_delete_video_links_not_from_cloudinary(
            self):
        """Because video urls don't have to be from Cloudinary, we should
        ensure that they can still be deleted the normal way. """

        dummy_property = PropertyFactory.create(
            video='http://www.videos.com/yeah',
            client=self.client1)

        url = reverse('property:delete_cloudinary_resource', args=[
                      dummy_property.slug])

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.user1.token}')
        update_data = {'image_others': [dummy_property.image_others[0]],
                       'video': dummy_property.video}
        response = self.client.delete(
            url, update_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data')['property']['video'], None)

    def test_that_regular_users_cannot_delete_images_of_a_property(self):
        """Regular users shouldn't be able to delete images of any property"""

        url = reverse('property:delete_cloudinary_resource', args=[
                      self.property11.slug])
        self.property11.is_published = True
        self.property11.save()
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.buyer1.token}')
        update_data = {'image_others': [self.property11.image_others[0]]}
        response = self.client.delete(
            url, update_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_we_get_appropriate_response_if_Cloudinary_fails_image_uploads(
            self):
        """If Cloudinary returns an error when uplaoding an image,
        we should return an appropriate response """
        uploader = Mock()
        uploader.upload.side_effects = Error

        temp_main_image = NamedTemporaryFile(suffix='.jpg')

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.user1.token}')

        data = self.property_data
        data['image_main'] = temp_main_image

        content = encode_multipart('BoUnDaRyStRiNg', data)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'

        res = self.client.post(self.create_list_url,
                               content, content_type=content_type)
        temp_main_image.close()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(res.data['errors'].get('image')),
                         ('Image is either corrupted or of an unkown format. '
                          'Please try again with a different image file.'))

    @patch('utils.media_handlers.uploader.upload_large')
    @patch('utils.media_handlers.uploader.upload')
    def test_that_client_admins_can_update_the_main_image_of_property(
            self, mock_upload, mock_video_upload):
        """When client admins update the main image of their property, the
        previous main image is not deleted, but instead added to the list of
        other images.
        THey can also update their videos, but the old one is deleted
        because they are only allowed to have one video per property page."""

        mock_upload.return_value = {'url': 'http://www.uploaded.com/'}
        mock_video_upload.return_value = {
            'url': 'http://www.video.uploaded.com/'}

        image_others_count = len(self.property11.image_others)
        current_video = self.property11.video
        url = reverse('property:single_property', args=[
                      self.property11.slug])

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.user1.token}')
        update_data = self.property_update
        update_data.pop('image_others')
        temp_image1 = NamedTemporaryFile(suffix='.png')
        temp_video = NamedTemporaryFile(suffix='.mp4')
        update_data['image_main'] = temp_image1
        update_data['video'] = temp_video
        content = encode_multipart('BoUnDaRyStRiNg', update_data)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'

        response = self.client.patch(
            url, content, content_type=content_type
        )
        temp_image1.close()
        temp_video.close()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('data')['property']['image_main'],
            'http://www.uploaded.com/')
        # the count of image_others increase by one
        self.assertEqual(
            len(response.data.get('data')['property']['image_others']),
            image_others_count + 1)
        # the new video is not the same as the old one
        self.assertFalse(
            response.data.get('data')['property']['video'] == current_video)

    @patch('utils.media_handlers.uploader.upload_large')
    def test_client_can_update_video_if_their_property_has_no_current_video(
            self, mock_video_upload):
        """Even if their property has no video, the client admins should still
        be able to update their property by uploading a new video """

        mock_video_upload.return_value = {
            'url': 'http://www.video.uploaded.com/'}

        url = reverse('property:single_property', args=[
                      self.property_no_images.slug])

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.user2.token}')

        update_data = self.property_update
        update_data.pop('image_others')

        temp_video = NamedTemporaryFile(suffix='.mp4')
        update_data['video'] = temp_video

        content = encode_multipart('BoUnDaRyStRiNg', update_data)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'

        response = self.client.patch(
            url, content, content_type=content_type
        )
        temp_video.close()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('data')['property']['video'],
            'http://www.video.uploaded.com/')

    def test_errors_from_cloudinary_video_upload_properly_handled(
            self):
        """Errors from Cloudinary video uploads should be returned
        in a more informative way. """

        temp_video = NamedTemporaryFile(suffix='.mp4')

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.user1.token}')

        data = self.property_data
        data['video'] = temp_video

        content = encode_multipart('BoUnDaRyStRiNg', data)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'

        with patch(
                'utils.media_handlers.uploader.upload_large') as mock_upload:
            mock_upload.side_effect = Error
            res = self.client.post(self.create_list_url,
                                   content, content_type=content_type)
        temp_video.close()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(res.data['errors'].get('video')),
                         ('Video is either corrupted or of an unkown format.'
                          'Please try again with a different video file.'))

    @patch('utils.media_handlers.uploader.upload')
    def test_users_cannot_upload_more_than_max_limit_when_creating_property(
            self, mock_upload):
        """
        There is a limit to the number of images each property can have.
        This test asserts that the limit is enforced when creating property.
        """

        mock_upload.return_value = {'url': 'http://main.image/upload'}

        files = []

        # we create image files reaching our limit of MAX_PROPERTY_IMAGE_COUNT
        while len(files) < MAX_PROPERTY_IMAGE_COUNT:
            image = NamedTemporaryFile(suffix='.jpg')
            files.append(image)

        temp_main_image = NamedTemporaryFile(suffix='.jpg')
        excess_image = NamedTemporaryFile(suffix='.jpg')
        # we pass an extra image, exceeding the MAX_PROPERTY_IMAGE_COUNT
        files.append(excess_image)

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.user1.token}')

        data = self.property_data
        data['image_main'] = temp_main_image
        data['image_others'] = files

        content = encode_multipart('BoUnDaRyStRiNg', data)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        res = self.client.post(self.create_list_url,
                               content, content_type=content_type)
        temp_main_image.close()
        for image in files:
            image.close()
        excess_image.close()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(res.data['errors'].get('image_others')),
                         ('Sorry. You are limited to a maximum of '
                          f'{MAX_PROPERTY_IMAGE_COUNT} images. '
                          'Please reduce the number of images you wish to '
                          'upload and try again.')
                         )

    @patch('utils.media_handlers.uploader.upload')
    def test_users_cannot_exceed_image_limit_when_updating_property(
            self, mock_upload):
        """When updating property, client admins should not exceed the
        limit for maximum images property are allowed to have. """

        mock_upload.return_value = {'url': 'http://www.uploaded.com/'}

        url = reverse('property:single_property', args=[
                      self.property11.slug])

        files = []
        # the property already has more than one image. If we create
        # images that are at the maximum limit, it means that sending
        # them should fail because we will have exceeded the maximum limit.
        while len(files) < MAX_PROPERTY_IMAGE_COUNT:
            image = NamedTemporaryFile(suffix='.jpg')
            files.append(image)

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.user1.token}')
        update_data = self.property_update

        update_data['image_others'] = files
        content = encode_multipart('BoUnDaRyStRiNg', update_data)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'

        response = self.client.patch(
            url, content, content_type=content_type
        )
        for image in files:
            image.close()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['errors'].get('image_others')),
                         ('Sorry. You are limited to a maximum of '
                          f'{MAX_PROPERTY_IMAGE_COUNT} images. '
                          'Please reduce the number of images you wish to '
                          'upload and try again.')
                         )

    def test_that_get_trending_properties_succeeds(self):
        """
        this methods tests that trending properties
        have to be pusblished and not sold
        """
        url = reverse('property:trending_property')
        url = url + '?city=Lagos'
        request = self.factory.get(url, format='json')
        force_authenticate(request, user=self.user1)
        view = TrendingPropertyView.as_view()
        response = view(request)
        self.assertEqual(response.data[0]['view_count'], 10)
        self.assertEqual(response.data[1]['view_count'], 4)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_trending_url_without_address(self):
        """
        this methods tests when a user provides
        a url without an address
        """

        url = reverse('property:trending_property')
        request = self.factory.get(url, format='json')
        force_authenticate(request, user=self.user1)
        view = TrendingPropertyView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data.get('errors')),
                         'Please specify a city')

    def test_trending_property_at_a_specific_time(self):
        """
        Since a user may want to search for
        a property that was trending at a specific time.
        this helps him or her to get the properties trending
        """
        url = reverse('property:trending_property')
        url = url + '?city=Lagos&date=2019-06-17'
        request = self.factory.get(url, format='json')
        force_authenticate(request, user=self.user1)
        view = TrendingPropertyView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BuyerPropertyListTest(BaseTest):
    """
    here we test the views arising from
    the BuyerPropertyList model.
    """

    def test_users_can_get_their_property_list(self):
        """we test if users can successfully obtain their lists """
        request = self.factory.get(
            self.get_buyer_list_url, format="json")
        force_authenticate(request, user=self.buyer1)
        view = BuyerPropertyListView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_users_can_add_property_to_their_buying_list(self):
        """
        we test if users can't add non_existent
        property to their buying list.
        """

        self.modify_buyer_list_url = reverse(
            'property:modify_buyer_list', args=[self.property4.slug])
        request = self.factory.post(
            self.modify_buyer_list_url, format="json")
        force_authenticate(request, user=self.buyer1)
        view = BuyerPropertyListView.as_view()
        response = view(request, self.property4.slug)
        self.assertIn(
            ' has been successfully added to your buy list',
            response.data['data'],
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_users_cant_delete_non_existent_property_from_list(self):
        """
        we test if users can delete non_existent
        property from their buying list.
        """
        self.modify_buyer_list_url = reverse(
            'property:modify_buyer_list', args=[self.property1.slug])
        request = self.factory.delete(
            self.modify_buyer_list_url, format="json")
        force_authenticate(request, user=self.buyer1)
        view = BuyerPropertyListView.as_view()
        response = view(request, self.property1.slug)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_users_cant_add_non_existent_property_to_list(self):
        """
        we test if users can't add non-exisiting
        property to their buying list.
        """
        self.modify_buyer_list_url = reverse(
            'property:modify_buyer_list', args=[self.property1.slug])
        request = self.factory.post(
            self.modify_buyer_list_url, format="json")
        force_authenticate(request, user=self.buyer1)
        view = BuyerPropertyListView.as_view()
        response = view(request, self.property1.slug)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get('errors'), 'Property not found')

    def test_users_cant_add_already_existing_property_to_their_buying_list(self):  # noqa
        """
        we test if users can't add already exisiting
        property to their buying list.
        """
        self.modify_buyer_list_url = reverse(
            'property:modify_buyer_list', args=[self.property4.slug])
        request = self.factory.post(
            self.modify_buyer_list_url, format="json")
        force_authenticate(request, user=self.buyer1)
        view = BuyerPropertyListView.as_view()
        response = view(request, self.property2.slug)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('errors'),
                         self.property2.title + ' is already in your buy list')

    def test_users_can_delete_already_existing_property_from_their_buying_list(self):  # noqa
        """
        we test if users can delete already
        exisiting property from their buying list.
        """
        self.modify_buyer_list_url = reverse(
            'property:modify_buyer_list', args=[self.property2.slug])
        request = self.factory.delete(
            self.modify_buyer_list_url, format="json")
        force_authenticate(request, user=self.buyer1)
        view = BuyerPropertyListView.as_view()
        response = view(request, self.property2.slug)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data'), self.property2.title  # noqa
                         + ' has been successfully removed from your buy list')

    def test_users_cant_delete_non_existing_property_from_their_buying_list(self):  # noqa
        """
        we test if users can't delete already exisiting
        property from their buying list.
        """
        self.modify_buyer_list_url = reverse(
            'property:modify_buyer_list', args=[self.property4.slug])
        request = self.factory.delete(
            self.modify_buyer_list_url, format="json")
        force_authenticate(request, user=self.buyer1)
        view = BuyerPropertyListView.as_view()
        response = view(request, self.property4.slug)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('errors'),
                         self.property4.title + ' is not in your buy list')


class TestEnquiryViews(BaseTest):

    def test_user_can_be_able_to_create_an_enquiry(self):
        """
        test that users can be able to enquire about a property
        """

        slug = self.property11.slug

        post_enquiry = self.factory.post(
            post_enquiry_url(slug), self.enquiry_data)
        force_authenticate(post_enquiry, user=self.user3)
        view = ListCreateEnquiryAPIView.as_view()
        resp = view(post_enquiry, property_slug=slug)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_non_user_cant_create_enquiries(self):
        """
        test that only users can create a property enquiry
        """


        slug = self.property11.slug

        post_enquiry = self.factory.post(
            post_enquiry_url(slug), self.enquiry_data)

        force_authenticate(post_enquiry, user=self.user1)
        view = ListCreateEnquiryAPIView.as_view()
        resp = view(post_enquiry, property_slug=slug)

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_that_a_user_cannot_create_enquiry_two_times(self):
        """
        Test a user cannot be able to create an enquiry
        two times if the one he has created has not already been resolved
        """


        slug = self.property11.slug

        post_enquiry = self.factory.post(
            post_enquiry_url(slug), self.enquiry_data)
        force_authenticate(post_enquiry, user=self.user3)
        view = ListCreateEnquiryAPIView.as_view()
        resp = view(post_enquiry, property_slug=slug)

        post_enquiry1 = self.factory.post(
            post_enquiry_url(slug), self.enquiry_data)
        force_authenticate(post_enquiry1, user=self.user3)
        view = ListCreateEnquiryAPIView.as_view()
        resp = view(post_enquiry1, property_slug=slug)

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('enquiry for this property already exists',
                      str(resp.data))

    def test_user_cannot_create_enquiry_with_a_past_date(self):
        """
        A user cannnot be able to post a date that is in the past as the visit
        date
        """


        slug = self.property11.slug

        post_enquiry = self.factory.post(
            post_enquiry_url(slug), self.enquiry_with_past_date)
        force_authenticate(post_enquiry, user=self.user3)
        view = ListCreateEnquiryAPIView.as_view()
        resp = view(post_enquiry, property_slug=slug)
        self.assertIn(
            'You cannot put a date in the past',
            str(resp.data))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_be_able_to_get_one_enquiry(self):
        """ test that users can be able to get one enquiry
        after they have posted the enquiry """

        slug = self.property11.slug

        post_enquiry = self.factory.post(
            post_enquiry_url(slug), self.enquiry_data)
        force_authenticate(post_enquiry, user=self.user3)
        view = ListCreateEnquiryAPIView.as_view()
        resp = view(post_enquiry, property_slug=slug)
        enquiry_id = resp.data['data']['enquiry_id']

        get_enquiry = self.factory.get(
            get_one_enquiry(enquiry_id), format='json'
        )
        self.user3.role = 'BY'
        self.user3.save()
        force_authenticate(get_enquiry, user=self.user3)
        view2 = PropertyEnquiryDetailView.as_view()
        get_response = view2(get_enquiry, enquiry_id=enquiry_id)
        self.assertIn('we-love-landville-we-love-landville',
                      str(get_response.data))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)

    def test_user_can_delete_an_enquiry(self):
        """ test users/buyer can be able to delete an enquiry """


        slug = self.property11.slug

        post_enquiry = self.factory.post(
            post_enquiry_url(slug), self.enquiry_data)
        force_authenticate(post_enquiry, user=self.user3)
        view = ListCreateEnquiryAPIView.as_view()
        resp = view(post_enquiry, property_slug=slug)
        enquiry_id = resp.data['data']['enquiry_id']

        delete_enquiry = self.factory.delete(
            get_one_enquiry(enquiry_id), format='json'
        )
        force_authenticate(delete_enquiry, user=self.user3)
        view2 = PropertyEnquiryDetailView.as_view()
        delete_response = view2(delete_enquiry, enquiry_id=enquiry_id)

        self.assertIn('Enquiry deleted successfully',
                      str(delete_response.data))
        self.assertEqual(delete_response.status_code,
                         status.HTTP_200_OK)

    def test_user_update_an_enquiry(self):
        """ test a user can be able to update an enquiry """

        slug = self.property11.slug

        post_enquiry = self.factory.post(
            post_enquiry_url(slug), self.enquiry_data)
        force_authenticate(post_enquiry, user=self.user3)
        view = ListCreateEnquiryAPIView.as_view()
        resp = view(post_enquiry, property_slug=slug)
        enquiry_id = resp.data['data']['enquiry_id']

        update_enquiry = self.factory.put(
            get_one_enquiry(enquiry_id), self.enquiry_data_update,
        )
        force_authenticate(update_enquiry, user=self.user3)
        view = PropertyEnquiryDetailView.as_view()
        up_res = view(update_enquiry, enquiry_id=enquiry_id)
        # lets now check if the new message is contained in the response
        self.assertIn('We are from Landville', str(up_res.data))
        self.assertEqual(up_res.status_code, status.HTTP_200_OK)

    def test_user_can_get_all_his_enquiries(self):
        """ 
        test that a user gets an empty list when there are no enquiries
        posted

        """

        get_enquiry = self.factory.get(
            GET_ALL_ENQURIES_URL, format='json'
        )
        self.user3.role = 'BY'
        self.user3.save()
        force_authenticate(get_enquiry, user=self.user3)
        view2 = ListCreateEnquiryAPIView.as_view()
        get_response = view2(get_enquiry)
        self.assertEqual(len(get_response.data['results']), 0)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)

    def test_landville_admin_can_be_able_to_get_all_records(self):
        """
        test landville admin can be able to get all enquiries
        not that since he is a landville admin, he can be able to get
        all the enquiries even the one posted in the propertyenquiry factory
         """
        get_enquiry = self.factory.get(
            GET_ALL_ENQURIES_URL, format='json'
        )
        self.user3.role = 'LA'
        self.user3.save()
        force_authenticate(get_enquiry, user=self.admin)
        view2 = ListCreateEnquiryAPIView.as_view()
        get_response = view2(get_enquiry)

        # the admin will be able to get the enquiry we posted in the factory
        self.assertEqual(len(get_response.data['results']), 1)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)

    def test_client_admin_can_be_able_to_get_enquiries_of_his_properties(self):
        """
        test client admin can be able
        to get enquiries about a property
        """
        get_enquiry = self.factory.get(
            GET_ALL_ENQURIES_URL, format='json'
        )

        force_authenticate(get_enquiry, user=self.user1)
        view2 = ListCreateEnquiryAPIView.as_view()
        get_response = view2(get_enquiry)
        # since no enquiries have been made so far lets assert the list is 0
        self.assertEqual(len(get_response.data['results']), 0)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)

    def test_landville_admin_can_be_able_to_get_one_one_enquiry(self):
        """ test landville admin can able to get one enquiry """

 
        slug = self.property11.slug

        post_enquiry = self.factory.post(
            post_enquiry_url(slug), self.enquiry_data)
        force_authenticate(post_enquiry, user=self.user3)
        view = ListCreateEnquiryAPIView.as_view()
        resp = view(post_enquiry, property_slug=slug)
        enquiry_id = resp.data['data']['enquiry_id']

        get_enquiry = self.factory.get(
            get_one_enquiry(enquiry_id), format='json'
        )

        force_authenticate(get_enquiry, user=self.admin)
        view2 = PropertyEnquiryDetailView.as_view()
        get_response = view2(get_enquiry, enquiry_id=enquiry_id)

        self.assertIn('we-love-landville-we-love-landville',
                      str(get_response.data))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)

    def test_user_cant_enquire_for_a_non_existent_propery(self):
        """ test a user cannot enquire about a non-existent property """

        slug = 'jkshskdhsdksdnskdskdshdskdh'

        post_enquiry = self.factory.post(
            post_enquiry_url(slug), self.enquiry_data)
        force_authenticate(post_enquiry, user=self.user3)
        view = ListCreateEnquiryAPIView.as_view()
        resp = view(post_enquiry, property_slug=slug)

        self.assertIn('we did not find the property', str(resp.data))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_client_admin_can_be_able_to_get_one_enquiry(self):
        """ test client admin cab be able to get a single enquiry """


        slug = self.property11.slug

        post_enquiry = self.factory.post(
            post_enquiry_url(slug), self.enquiry_data)
        force_authenticate(post_enquiry, user=self.user3)
        view = ListCreateEnquiryAPIView.as_view()
        resp = view(post_enquiry, property_slug=slug)
        enquiry_id = resp.data['data']['enquiry_id']

        get_enquiry = self.factory.get(
            get_one_enquiry(enquiry_id), format='json'
        )

        force_authenticate(get_enquiry, user=self.user1)
        view2 = PropertyEnquiryDetailView.as_view()
        get_response = view2(get_enquiry, enquiry_id=enquiry_id)
        self.assertIn('we-love-landville-we-love-landville',
                      str(get_response.data))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
