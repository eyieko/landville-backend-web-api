from unittest.mock import patch
from authentication.models import User

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.serializers import ValidationError
from authentication.serializers import (
    FacebookAuthAPISerializer, GoogleAuthSerializer, TwitterAuthAPISerializer)


GOOGLE_VALIDATION = "authentication.socialvalidators.SocialValidation.google_auth_validation"
FACEBOOK_VALIDATION = "authentication.socialvalidators.SocialValidation.facebook_auth_validation"
TWITTER_VALIDATION = "authentication.socialvalidators.SocialValidation.twitter_auth_validation"


def sample_user():
    return get_user_model().objects.create_user(email='cmeordvda_1554574357@tfbnw.net',
                                                first_name='cmeordvda',
                                                last_name="kelvo",
                                                password='T35tP45w0rd'
                                                )


class GoogleSerializerTest(TestCase):
    """
    Unit test for the GoogleSerializer
    class defined in our serializers.
    """

    def setUp(self):
        self.payload = {
            "access_token": "access_token"
        }

    def test_valid_google_login(self):
        with patch(GOOGLE_VALIDATION) as mg:
            mg.return_value = {
                "name": "alexa onkundi",
                "email": "alexa@gmail.com",
                "sub": "102723377587866"
            }
            serializer = GoogleAuthSerializer(data=self.payload)
            self.assertTrue(serializer.is_valid())

    def test_valid_google_login_with_image(self):
        with patch(GOOGLE_VALIDATION) as mg:
            mg.return_value = {
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
            self.assertTrue(serializer.is_valid())

    def test_in_valid_google_login(self):
        serializer = GoogleAuthSerializer(data=self.payload)
        self.assertFalse(serializer.is_valid())

    def test_login_user_already_exist(self):
        sample_user()
        with patch(GOOGLE_VALIDATION) as mg:
            mg.return_value = {
                "name": "alexa amazon",
                "email": "alexa@gmail.com",
                "sub": "102723377587866"
            }
            serializer = GoogleAuthSerializer(data=self.payload)
            self.assertTrue(serializer.is_valid())
            self.assertIn('access_token', str(serializer))


class FacebookSerializerTest(TestCase):
    """
    Unit test for the FacebookSerializer
    class defined in our serializers.
    """

    def setUp(self):
        self.payload = {
            "access_token": "access_token"
        }

    def test_valid_facebook_login(self):
        with patch(FACEBOOK_VALIDATION) as mg:
            mg.return_value = {
                "first_name": "alexa",
                "last_name": "amazon",
                "email": "alexa@gmail.com",
                "id": "102723377587866"
            }
            serializer = FacebookAuthAPISerializer(data=self.payload)
            self.assertTrue(serializer.is_valid())

    def test_valid_facebook_login_with_image(self):
        with patch(FACEBOOK_VALIDATION) as mg:
            mg.return_value = {
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

    def test_in_valid_facebook_login(self):
        serializer = FacebookAuthAPISerializer(data=self.payload)
        self.assertFalse(serializer.is_valid())

    def test_login_user_already_exist(self):
        sample_user()
        with patch(FACEBOOK_VALIDATION) as mg:
            mg.return_value = {
                'email': 'cmeordvda_1554574357@tfbnw.net',
                'first_name': 'cmeordvda',
                'last_name': "kelvo",
                "id": "102723377587866"
            }
            serializer = FacebookAuthAPISerializer(data=self.payload)
            self.assertTrue(serializer.is_valid())
            self.assertIn('access_token', str(serializer))
