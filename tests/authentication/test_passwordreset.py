from unittest.mock import patch

from django.urls import reverse
from rest_framework import status

from tests.authentication.test_base import PasswordResetTokenTestBase
from utils.resethandler import ResetHandler


class PasswordResetTest(PasswordResetTokenTestBase):

    def get_change_password_url(
            self, token, url=reverse('authentication:password-reset')):
        """ function for generating a url with token"""
        return url + '?token=' + token

    @patch('utils.tasks.send_email_notification.delay')
    def test_user_gets_reset_token(self, mock_email):
        """ test a user gets a reset link """
        mock_email.return_value = True
        response = self.client.post(
            self.reset_password_url, self.valid_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('If you have an account with us we have sent an email',
                      response.data.get('data')['message'])

    @patch('utils.tasks.send_email_notification.delay')
    def test_user_get_response_if_user_non_existent(self, mock_email):
        """ test user still gets a response even if the user does not exist """
        mock_email.return_value = True
        response = self.client.post(
            self.reset_password_url, self.invalid_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            "If you have an account with us we have sent an email to",
            response.data.get('data')['message'])

    @patch('utils.tasks.send_email_notification.delay')
    def test_users_can_reset_passwords_successfully(self, mock_email):
        """ given valid data, test if users can reset their passwords. """
        mock_email.return_value = True
        url = self.get_change_password_url(self.reset_token)
        response = self.client.patch(
            url, self.valid_passwords, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('data')['message'],
            'password has been changed successfully')

    @patch('utils.tasks.send_email_notification.delay')
    def test_error_when_user_passes_invalid_token(self, mock_email):
        """ test if an exception is raised when user passes in an invalid
        token."""
        mock_email.return_value = True
        url = self.get_change_password_url(self.reset_token)
        self.client.patch(
            url, self.valid_passwords, format="json")
        response = self.client.patch(
            url, self.valid_passwords, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'This token is no longer valid, please get a',
            str(response.data['errors']['token'][0]))

    @patch('utils.tasks.send_email_notification.delay')
    def test_error_when_user_passes_expired_token(self, mock_email):
        """ test if an exception is thrown when a user passes an expired
        token """
        mock_email.return_value = True
        url = self.get_change_password_url(self.expired_token)
        response = self.client.patch(
            url, self.valid_passwords, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            str(response.data['errors']['detail']),
            'Your token has expired. Make a new token and try again')

    @patch('utils.tasks.send_email_notification.delay')
    def test_error_when_user_passes_a_token_with_wrong_format(self,
                                                              mock_email):
        """ 
        tokens have specific formats, this tests if an error
        is thrown if a user passes a token with wrong format
        """
        mock_email.return_value = True
        url = self.get_change_password_url(self.fake_token)
        response = self.client.patch(
            url, self.valid_passwords, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data['errors']['token'][0]),
            'Error. Could not decode token!')

    @patch('utils.tasks.send_email_notification.delay')
    def test_error_when_token_belonging_to_non_existent_user_is_passed(self,
                                                                       mock_email):
        """
        consider this: a user generates a password reset link,
        then by other measures, the user's account is deleted from
        our database, this tests if an exception is thrown in such cases.
        this answers the question: "how did the token be generated in the
        first place?"
        """
        mock_email.return_value = True
        url = self.get_change_password_url(self.non_existent_user_token)
        response = self.client.patch(
            url, self.valid_passwords, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            str(response.data['errors']['detail']),
            'User matching this token was not found.')

    @patch('utils.tasks.send_email_notification.delay')
    def test_error_when_a_non_dicitionary_is_passed(self, mock_email):
        """ test is an error is thrown if a non-dictionary is passed. """
        mock_email.return_value = True
        with self.assertRaises(TypeError) as e:
            ResetHandler().create_verification_token(self.faker.text())
        self.assertEqual(str(e.exception), 'Payload must be a dictionary!')

    @patch('utils.tasks.send_email_notification.delay')
    def test_error_when_unmatching_password_pair_passed(self, mock_email):
        """ test if an exception is thrown when unmatching passwords passed.
        """
        mock_email.return_value = True
        url = self.get_change_password_url(self.reset_token)
        response = self.client.patch(
            url, self.unmatching_passwords, format="json")
        self.assertEqual(
            str(response.data['errors']['error'][0]), 'passwords do not match')
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('utils.tasks.send_email_notification.delay')
    def test_error_when_non_existent_token_passed(self, mock_email):
        """ test if an error is thrown when a non-existent password is
        passed. """
        mock_email.return_value = True
        url = self.get_change_password_url(self.faker.text())
        response = self.client.patch(
            url, self.unmatching_passwords, format="json")
        self.assertEqual(
            str(response.data['errors']['token'][0]),
            "We couldn't find such token in our database")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('utils.tasks.send_email_notification.delay')
    def test_error_when_user_suppplies_weak_password(self, mock_email):
        """ test if error is thrown when a user supplies weak password. """
        mock_email.return_value = True
        url = self.get_change_password_url(self.reset_token)
        response = self.client.patch(
            url, self.weak_password, format="json")
        self.assertEqual(
            str(response.data['errors']['password'][0]),
            'This password is too common.')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
