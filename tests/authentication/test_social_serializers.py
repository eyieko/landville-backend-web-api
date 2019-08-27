import json
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase
from authentication.serializers import (
    FacebookAuthAPISerializer, GoogleAuthSerializer, TwitterAuthAPISerializer)
from facebook import GraphAPIError
from collections import namedtuple
from authentication.socialvalidators import SocialValidation


FACEBOOK_VALIDATION = "authentication.socialvalidators"
FACEBOOK_VALIDATION += ".SocialValidation.facebook_auth_validation"
TWITTER_VALIDATION = "authentication.socialvalidators.SocialValidation"
TWITTER_VALIDATION += ".twitter_auth_validation"


def sample_user():
    return get_user_model().\
        objects.create_user(email='cmeordvda_1554574357@tfbnw.net',
                            first_name='cmeordvda',
                            last_name="kelvo",
                            password='T35tP45w0rd')

class BaseTest(TestCase):
    """
    base class to be used by other tests
    """
    def setUp(self):
        self.payload = {"access_token": "access_token"}


class GoogleSerializerTest(BaseTest):
    """
    Unit test for the GoogleSerializer
    class defined in our serializers.
    """

    def setUp(self):
        self.payload = {
            "access_token": "access_token"
        }

    @patch('authentication.socialvalidators.id_token.verify_oauth2_token')
    def test_valid_google_login(self, mock_google):
        mock_google.return_value = {
                "name": "alexa onkundi",
                "email": "alexa@gmail.com",
                "sub": "102723377587866"
            }
        serializer = GoogleAuthSerializer(data=self.payload)
        self.assertIsNotNone(serializer.validate(self.payload))
        self.assertTrue(serializer.is_valid())

    @patch('authentication.socialvalidators.id_token.verify_oauth2_token')
    def test_valid_google_login_with_image(self, mock_google):
        mock_google.return_value = {
                "name": "pixa amandlan",
                "email": "amandlan@gmail.com",
                "sub": "1027232332187866",
                "picture":
                "https://platform-lookaside.fbsbx.com/" +
                "platform/profilepic/?asid=24700904930486" +
                "75&height=50&width=50&ext=1565377096&hash" +
                "=AeRPETSPqmmN8yZQ"
            }
        serializer = GoogleAuthSerializer(data=self.payload)
        self.assertIsNotNone(serializer.validate(self.payload))
        self.assertTrue(serializer.is_valid())

    @patch('authentication.socialvalidators.id_token.verify_oauth2_token')
    def test_invalid_google_login(self, mock_google):
        mock_google.side_effect = ValueError
        serializer = GoogleAuthSerializer(data=self.payload)
        self.assertFalse(serializer.is_valid())

    @patch('authentication.socialvalidators.id_token.verify_oauth2_token')
    def test_login_user_already_exist(self, mock_google):
        sample_user()
        mock_google.return_value = {
                "name": "alexa amazon",
                "email": "alexa@gmail.com",
                "sub": "102723377587866"
            }
        serializer = GoogleAuthSerializer(data=self.payload)
        self.assertTrue(serializer.is_valid())
        self.assertIn('access_token', str(serializer))


class FacebookSerializerTest(BaseTest):
    """
    Unit test for the FacebookSerializer
    class defined in our serializers.
    """

    @patch('authentication.socialvalidators.GraphAPI.request')
    def test_valid_facebook_login(self, mock_facebook):
        mock_facebook.return_value = {
                "first_name": "alexa",
                "last_name": "amazon",
                "email": "alexa@gmail.com",
                "id": "102723377587866"
            }
        serializer = FacebookAuthAPISerializer(data=self.payload)
        self.assertTrue(serializer.is_valid())

    @patch('authentication.socialvalidators.GraphAPI.request')
    def test_valid_facebook_login_with_image(self, mock_facebook):
        mock_facebook.return_value = {
                "first_name": "pixa",
                "last_name": "amandla",
                "email": "alexan@gmail.com",
                "id": "102723377587866",
                "picture": {
                    "data": {
                        "url": "https://platform-lookaside.fbsbx.com/" +
                        "platform/profilepic/?asid=24700904930486" +
                        "75&height=50&width=50&ext=1565377096&hash" +
                        "=AeRPETSPqmmN8yZQ"
                    }
                }
            }
        serializer = FacebookAuthAPISerializer(data=self.payload)
        self.assertTrue(serializer.is_valid())

    @patch('authentication.socialvalidators.GraphAPI')
    def test_invalid_facebook_login(self, mock_facebook):
        mock_facebook.side_effect = GraphAPIError('Invalid data')
        serializer = FacebookAuthAPISerializer(data=self.payload)
        self.assertFalse(serializer.is_valid())

    @patch('authentication.socialvalidators.GraphAPI.request')
    def test_login_user_already_exist(self, mock_facebook):
        sample_user()
        mock_facebook.return_value = {
                'email': 'cmeordvda_1554574357@tfbnw.net',
                'first_name': 'cmeordvda',
                'last_name': "kelvo",
                "id": "102723377587866"
            }
        serializer = FacebookAuthAPISerializer(data=self.payload)
        self.assertTrue(serializer.is_valid())
        self.assertIn('access_token', str(serializer))


class TestTwitterSerializer(BaseTest):

    """
    class that test serializers for twitter authentication
    """

    @patch('authentication.socialvalidators.OAuth1Session.get')
    def test_valid_twitter_login(self, mock_twitter):
        data = self.payload.copy()
        data["access_token_secret"] = "a fake secret"
        payloads = json.dumps({
            "name":
            "alexa amazon",
            "email":
            "alexa@gmail.com",
            "id":
            "102723377587866",
            "id_str":
            'test-user12345',
            "profile_image_url_https": "test profile"
        })
        mocked_response = namedtuple('response', ['text', 'json'])
        mock_twitter.return_value = mocked_response(text=payloads, json={})
        serializer = TwitterAuthAPISerializer(data=data)
        self.assertTrue(serializer.is_valid())

    @patch('authentication.socialvalidators.OAuth1Session.get')
    def test_invalid_twitter_login(self, mock_twitter):
        data = self.payload.copy()
        data["access_token_secret"] = "a fake secret"
        mock_twitter.side_effect = Exception
        self.assertIsNone(
            SocialValidation.twitter_auth_validation(
                data.get('access_token'), data.get('access_token_secret')))

    @patch('authentication.socialvalidators.OAuth1Session.get')
    def test_valid_twitter_login_failed_with_serializer(self, mock_twitter):
        data = self.payload.copy()
        data["access_token_secret"] = "a fake secret"
        payloads = json.dumps({
            "errors": [{'message': 'invalid data'}]
        })
        mocked_response = namedtuple('response', ['text', 'json'])
        mock_twitter.return_value = mocked_response(text=payloads, json={})
        serializer = TwitterAuthAPISerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(str(serializer.errors.get('errors')[0]),
                         'invalid data')
