
"""Contains the setup method for login tests."""

from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from authentication.models import User
from tests.factories.authentication_factory import UserFactory


class BaseTest(APITestCase):
    """Set up the testing client."""

    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse("auth:login")
        self.logout_url = reverse("auth:logout")
        self.client_profile = reverse("auth:profile")
        self.user = User.objects.create_user(first_name="Firstname", email="spanish@test.com",
                                             last_name="LastName",
                                             password="Password~!Z")
        self.user.is_verified = True
        self.user.save()
