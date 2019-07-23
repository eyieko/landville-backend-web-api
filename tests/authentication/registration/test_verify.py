
"""User email verification tests."""
from datetime import (
    datetime,
    timedelta,
)
from unittest.mock import patch
from django.urls import reverse

import jwt
from django.conf import settings
from rest_framework import status

from tests.authentication.registration.test_base import BaseTest


class UserEmailVerificationTest(BaseTest):
    """Contains user email verification test methods."""

    @patch('utils.tasks.send_email_notification.delay')
    def test_should_verify_a_user_successfully(self, mock_email):
        """Tests if a user can be activated successfuly."""
        mock_email.return_value = True
        self.client.post(
            self.registration_url, self.new_user, format="json")

        response = self.client.get(self.verify_url+"?token=" + jwt.encode(
            {"email": self.new_user["email"]}, settings.SECRET_KEY,
            algorithm="HS256").decode("utf-8")+"~6")

        self.assertEqual(
            response.status_code, status.HTTP_302_FOUND)

    @patch('utils.tasks.send_email_notification.delay')
    def test_user_cant_activate_with_expired_token(self, mock_email):
        """Test should not activate an account when the link is expired."""
        mock_email.return_value = True
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

        response = self.client.get(reverse('auth:verify') +
                                   "?token="+invalid_token, format="json")
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
