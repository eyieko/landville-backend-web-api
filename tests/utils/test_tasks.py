from unittest.mock import patch

from django.core.mail import EmailMultiAlternatives
from django.test import TestCase

from tests.factories.authentication_factory import UserFactory
from utils.tasks import send_email_notification


class CeleryTest(TestCase):

    def setUp(self):
        self.user = UserFactory.create()
        self.email_body = {
            "subject": "Test Status",
            "recipient": [self.user.email+"m"],
            "text_body": "email/authentication/base_email.txt",
            "html_body": "email/authentication/base_email.html",
            "context": {
                'title': "Hey there,",
                'message': "test"
            }
        }

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_handle_sending_email(self, mock_email):
        """
        Test Handling sending of notifications to the user via email
        :return: bool
        """
        mock_email.return_value = True

        send_email_notification(self.email_body)
        self.assertTrue(EmailMultiAlternatives.send.has_been_called)