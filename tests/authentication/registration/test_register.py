"""User registration tests."""
from .test_base import BaseTest
from rest_framework import status


class UserRegistrationTest(BaseTest):
    """Contains user registration test methods."""

    def test_user_should_register(self):
        """Create an account."""
        response = self.client.post(
            self.registration_url, self.new_user, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_should_not_register_with_invalid_email(self):
        """Create an account with an invalid email."""
        response = self.client.post(
            self.registration_url, self.invalid_email_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data["errors"]["email"][0]),
                         "Enter a valid email address.")

    def test_user_should_not_register_with_a_taken_email(self):
        """Create an account with a taken email"""
        self.client.post(
            self.registration_url, self.new_user, format="json")
        response = self.client.post(
            self.registration_url, self.new_user, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data["errors"]["email"][0]),
                         "user with this email already exists.")

    def test_user_should_not_register_with_a_weak_password(self):
        """Create an account with a weak password."""
        response = self.client.post(
            self.registration_url, self.weak_password_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response.data["errors"]["password"])

    def test_user_should_not_register_with_unmatching_passwords(self):
        """Create an account with passwords that donot match."""
        response = self.client.post(
            self.registration_url, self.umatching_passwords_data,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response.data["errors"]["passwords"])

    def test_user_should_not_register_with_no_first_name(self):
        """Create an account with no firstname."""
        response = self.client.post(
            self.registration_url, self.missing_firstname_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response.data["errors"]["first_name"])

    def test_user_should_not_register_with_no_lastname(self):
        """Create an account with no lastname."""
        response = self.client.post(
            self.registration_url, self.missing_lastname_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response.data["errors"]["last_name"])

    def test_user_should_not_register_with_an_empty_lastname(self):
        """Create an account with an empty lastname."""
        response = self.client.post(
            self.registration_url, self.empty_last_name_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response.data["errors"]["last_name"])

    def test_user_should_not_register_with_an_empty_firstname(self):
        """Create an account with an empty firstname."""
        response = self.client.post(
            self.registration_url, self.empty_firstname_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response.data["errors"]["first_name"])

    def test_user_should_not_register_with_an_empty_role(self):
        """Create an account with an empty role."""
        response = self.client.post(
            self.registration_url, self.invalid_role_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response.data["errors"]["role"])

    def test_user_should_not_register_as_admin(self):
        """Users should not be able to register as LandVille admins"""

        data = self.new_user
        data['role'] = 'LA'
        response = self.client.post(
            self.registration_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('"LA" is not a valid choice.', str(
            response.data['errors'].get('role')[0]))
