from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


FACEBOOK_URL = reverse('authentication:facebook')
GOOGLE_URL = reverse('authentication:google')
TWITTER_URL = reverse('authentication:twitter')


GOOGLE_VALIDATION = "authentication.socialvalidators.SocialValidation.google_auth_validation"
FACEBOOK_VALIDATION = "authentication.socialvalidators.SocialValidation.facebook_auth_validation"
TWITTER_VALIDATION = "authentication.socialvalidators.SocialValidation.twitter_auth_validation"


def sample_user():
    return get_user_model().objects.create_user(email='cmeordvda_1554574357@tfbnw.net',
                                                username='cmeordvda',
                                                password='T35tP45w0rd'
                                                )


class SocialAuthTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.facebook_payload = {
            "facebook": {
                "access_token": "valid token for facebook"
            }
        }
        self.google_payload = {
            "google": {
                "access_token": "valid token for google"
            }
        }
        self.twitter_payload = {
            "twitter": {
                "access_token": "valid token for twitter",
                "access_token_secret": "valid token for twitter"
            }
        }

    def test_facebook_login_valid_token(self):
        with patch(FACEBOOK_VALIDATION) as mf:
            mf.return_value = {
                "name": "kelvin onkundi",
                "email": "bcmeordvda_1554574357@tfbnw.net",
                "id": "102723377587866"}
            res = self.client.post(
                FACEBOOK_URL,
                self.facebook_payload,
                format='json')
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertIn("token", res.data)

    def test_facebook_login_invalid_token(self):
        res = self.client.post(
            FACEBOOK_URL,
            self.facebook_payload,
            format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Token is not valid.', str(res.data))

    def test_google_login_valid_token(self):
        with patch(GOOGLE_VALIDATION) as mg:
            mg.return_value = {
                "name": "Kelvin Onkundi",
                "email": "ndemokelvinonkundi@gmail.com",
                "sub": "102723377587866"
            }
            res = self.client.post(
                GOOGLE_URL,
                self.google_payload,
                format='json')
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertIn("token", res.data)

    def test_google_login_invalid_token(self):
        res = self.client.post(
            GOOGLE_URL,
            self.google_payload,
            format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('token is not valid', str(res.data))

    def test_twitter_login_valid_token(self):
        with patch(TWITTER_VALIDATION) as mg:
            mg.return_value = {
                "name": "kelvin onkundi",
                "email": "kelvin@gmail.com",
                "id_str": "102723377587866"
            }
            res = self.client.post(
                TWITTER_URL,
                self.twitter_payload,
                format='json')
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertIn("token", res.data)

        with patch(TWITTER_VALIDATION) as mg:
            mg.return_value = {
                "name": "kelvin onkundi",
                "email": "kelvin@gmail.com",
                "id_str": "102723377587866"
            }
            res = self.client.post(
                TWITTER_URL,
                self.twitter_payload,
                format='json')
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertIn("token", res.data)

    def test_twitter_login_invalid_token(self):
        res = self.client.post(
            TWITTER_URL,
            self.twitter_payload,
            format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid or expired token.', str(res.data))
