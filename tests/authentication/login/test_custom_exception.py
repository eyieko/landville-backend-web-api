from utils.exception_handler import custom_exception_handler
from django.test import TestCase
from rest_framework.exceptions import NotAuthenticated
from authentication.views import LoginAPIView


class AuthResponseTestCase(TestCase):
    """Contains the test for the custom exception response handler"""

    def test_custom_exception_handler(self):
        context = {"view": LoginAPIView}
        response = custom_exception_handler(
            NotAuthenticated({'invalid': 'invalid email and password combination'}), context)
        self.assertEqual(response.status_code, 401)
