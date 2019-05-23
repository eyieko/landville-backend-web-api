
from rest_framework.test import APIClient, APITestCase
from django.urls import reverse


class BaseTest(APITestCase):
    """Set up the testing client."""

    def setUp(self):
        self.client = APIClient()
        self.registration_url = reverse("auth:register")
        self.verify_url = reverse("auth:verify")
