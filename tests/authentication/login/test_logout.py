"""Contains user logout tests"""

from .test_base import BaseTest
from authentication.models import User
from rest_framework import status


class LogoutTest(BaseTest):
    """
    Tests user logout
    """

    def test_user_logout_successfully(self):
        """
        Authenticated users should be able to logout successfully
        """

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.user.token}')

        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["data"]["message"],
            "Successfully logged out"
        )

    def test_logged_out_user_has_no_access(self):
        """
        Test that logged out users have no access to authorized endpoints.
        for example,
        Logged out users should not be able to view their profile
        """
        token = self.user.token
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {token}')

        self.client.post(self.logout_url)
        response = self.client.get(self.client_profile)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(
            response.data["errors"]['detail'],
            "Session Expired."
        )
