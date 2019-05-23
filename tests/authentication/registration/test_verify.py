
"""User email verification tests."""
from .test_base import BaseTest
from .test_data import expired_token, valid_user_data, invalid_token
import jwt
from django.conf import settings
from authentication.models import User


class UserEmailVerificationTest(BaseTest):
    """Contains user email verification test methods."""

    def test_should_verify_a_user_successfully(self):
        """Tests if a user can be activated successfuly."""
        self.client.post(
            self.registration_url, valid_user_data, format="json")
        response = self.client.get(self.verify_url+"?token=" + jwt.encode(
            {"email": valid_user_data["email"]}, settings.SECRET_KEY,
            algorithm="HS256").decode("utf-8")+"~6")
        self.assertEqual(
            response.status_code, 200)

    def test_user_cant_activate_with_expired_token(self):
        """Test should not activate an account when the link is expired."""
        User.objects.create(id=1, email="email@email.com",
                            first_name="myname", last_name="test",
                            password="yt679866gv")
        response = self.client.get(
            self.verify_url+"?token="+expired_token, format="json")
        self.assertEqual(response.status_code, 200)

    def test_user_cant_not_activate_twice(self):
        """Test should not activate an account twice."""
        user = User.objects.create(id=1, email="email@email.com",
                                   first_name="myname",
                                   last_name="test",
                                   password="yt679866gv")
        user.is_verified = True
        user.save()
        response = self.client.get(self.verify_url+"?token="+jwt.encode(
            {"email": user.email}, settings.SECRET_KEY).decode("utf-8")+"~1", format="json")
        self.assertEqual(response.status_code, 200)

    def test_user_cant_activate_with_invalid_token(self):
        """Test should not activate an account with an invalid token."""
        response = self.client.get(
            self.verify_url+"?token="+invalid_token, format="json")
        self.assertEqual(response.status_code, 400)
