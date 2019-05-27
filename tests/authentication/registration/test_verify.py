
"""User email verification tests."""
from .test_base import BaseTest
import jwt
from django.conf import settings
from datetime import datetime, timedelta
from authentication.models import User
from rest_framework import status


class UserEmailVerificationTest(BaseTest):
    """Contains user email verification test methods."""

    def test_should_verify_a_user_successfully(self):
        """Tests if a user can be activated successfuly."""
        self.client.post(
            self.registration_url, self.new_user, format="json")
        response = self.client.get(self.verify_url+"?token=" + jwt.encode(
            {"email": self.new_user["email"]}, settings.SECRET_KEY,
            algorithm="HS256").decode("utf-8")+"~6")
        self.assertEqual(
            response.status_code, status.HTTP_200_OK)

    def test_user_cant_activate_with_expired_token(self):
        """Test should not activate an account when the link is expired."""
        expired_token = jwt.encode({"email": self.user.email, "exp": datetime.utcnow() -
                                    timedelta(hours=23)}, settings.SECRET_KEY).decode("utf-8")+"~"+str(self.user.id)
        response = self.client.get(
            self.verify_url+"?token="+expired_token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cant_not_activate_twice(self):
        """Test should not activate an account twice."""
        self.user.is_verified = True
        self.user.save()
        response = self.client.get(self.verify_url+"?token="+jwt.encode(
            {"email": self.user.email}, settings.SECRET_KEY).decode("utf-8")+"~1", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cant_activate_with_invalid_token(self):
        """Test should not activate an account with an invalid token."""
        invalid_token = jwt.encode({"email": self.user.email, "exp": datetime.utcnow() -
                                    timedelta(hours=23)}, settings.SECRET_KEY).decode("utf-8")+"1~"+str(self.user.id)

        response = self.client.get(
            self.verify_url+"?token="+invalid_token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
