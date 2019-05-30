"""Contains user login tests"""

from .test_base import BaseTest
from authentication.models import User
from rest_framework import status


class LoginTest(BaseTest):
    "Contains user login tests"

    def test_should_user_login_successfully(self):
        response = self.client.post(self.login_url, {
            "email": self.user.email,
            "password": "Password~!Z"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["status"], "success")
        self.assertIsNotNone(response.data["data"]["user"]["token"])

    def test_should_fail_with_invalid_password(self):
        response = self.client.post(self.login_url, {
            "email": self.user.email,
            "password": "Password~!Z1"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsNotNone(response.data["invalid"])

    def test_should_fail_with_an_unverified_email(self):
        self.user.is_verified = False
        self.user.save()
        response = self.client.post(self.login_url, {
            "email": self.user.email,
            "password": "Password~!Z"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsNotNone(response.data["user"])
