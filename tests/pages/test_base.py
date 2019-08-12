from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from pages.models import Term


class TermsTestBase(APITestCase):
    """Tests if users can view terms and conditions. """

    def setUp(self):
        self.terms_url = reverse("terms:terms")
        self.terms = Term.objects.create(
            details="You are not allowed to masquarade")
