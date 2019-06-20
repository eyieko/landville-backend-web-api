from django.test import TestCase
from tests.factories.authentication_factory import UserFactory


class BaseTest(TestCase):
    """Base class for admin forms tests."""

    def setUp(self):
        """Add variables that are used by test methods."""
        self.user = UserFactory.create()
        self.valid_user_data = {
            "password1": self.user.password,
            "password2": self.user.password,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email + "m"
        }
        self.invalid_user_data = {"password1": "", "password2": ""}
