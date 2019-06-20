from tests.authentication.test_base import PasswordResetTokenTestBase
from django.urls import reverse
from rest_framework import status
from utils.resethandler import ResetHandler


class PasswordResetTest(PasswordResetTokenTestBase):

    def get_change_password_url(self, token, url=reverse('authentication:password-reset')):
        """ function for generating a url with token"""
        return url+'?token='+token

    def test_user_gets_reset_token(self):
        """ test a user gets a reset link """
        response = self.client.post(
            self.reset_password_url, self.valid_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data')[
                         'message'], 'If you have an account with us we have sent an email to reset your password')

    def test_user_get_response_if_user_non_existent(self):
        """ test user still gets a response even if the user does not exist """
        response = self.client.post(
            self.reset_password_url, self.invalid_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data')[
                         'message'], 'If you have an account with us we have sent an email to reset your password')

    def test_users_can_reset_passwords_successfully(self):
        """ given valid data, test if users can reset their passwords. """
        url = self.get_change_password_url(self.reset_token)
        response = self.client.patch(
            url, self.valid_passwords, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data')[
                         'message'], 'password has been changed successfully')

    def test_error_when_user_passes_invalid_token(self):
        """ test if an exception is raised when user passes in an invalid token."""
        url = self.get_change_password_url(self.reset_token)
        self.client.patch(
            url, self.valid_passwords, format="json")
        response = self.client.patch(
            url, self.valid_passwords, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data["errors"]['token'][0]),
                         'This token is no longer valid, please get a new one')

    def test_error_when_user_passes_expired_token(self):
        """ test if an exception is thrown when a user passes an expired token """
        url = self.get_change_password_url(self.expired_token)
        response = self.client.patch(
            url, self.valid_passwords, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(str(response.data['errors']['detail']),
                         'Your token has expired. Make a new token and try again')

    def test_error_when_user_passes_a_token_with_wrong_format(self):
        """ 
        tokens have specific formats, this tests if an error
        is thrown if a user passes a token with wrong format
        """
        url = self.get_change_password_url(self.fake_token)
        response = self.client.patch(
            url, self.valid_passwords, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data["errors"]['token'][0]), 'Error. Could not decode token!')

    def test_error_when_token_belonging_to_non_existent_user_is_passed(self):
        """
        consider this: a user generates a password reset link,
        then by other measures, the user's account is deleted from 
        our database, this tests if an exception is thrown in such cases.
        this answers the question: "how did the token be generated in the first
        place?"
        """
        url = self.get_change_password_url(self.non_existent_user_token)
        response = self.client.patch(
            url, self.valid_passwords, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            str(response.data['errors']['detail']), 'User matching this token was not found.')

    def test_error_when_a_non_dicitionary_is_passed(self):
        """ test is an error is thrown if a non-dictionary is passed. """
        with self.assertRaises(TypeError) as e:
            ResetHandler().create_verification_token(self.faker.text())
        self.assertEqual(str(e.exception), 'Payload must be a dictionary!')

    def test_error_when_unmatching_password_pair_passed(self):
        """ test if an exception is thrown when unmatching passwords passed. """
        url = self.get_change_password_url(self.reset_token)
        response = self.client.patch(
            url, self.unmatching_passwords, format="json")
        self.assertEqual(
            str(response.data["errors"][0]), 'passwords do not match')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_error_when_non_existent_token_passed(self):
        """ test if an error is thrown when a non-existent password is passed. """
        url = self.get_change_password_url(self.faker.text())
        response = self.client.patch(
            url, self.unmatching_passwords, format="json")
        self.assertEqual(str(
            response.data["errors"]['token'][0]), "We couldn't find such token in our database")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_error_when_user_suppplies_weak_password(self):
        """ test if error is thrown when a user supplies weak password. """
        url = self.get_change_password_url(self.reset_token)
        response = self.client.patch(
            url, self.weak_password, format="json")
        self.assertEqual(
            str(response.data["errors"]['password'][0]), 'This password is too common.')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
