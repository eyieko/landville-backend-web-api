"""User registration tests."""
from .test_base import BaseTest
from .test_data import (valid_user_data, umatching_passwords_data,
                        invalid_email_data, weak_password_data,
                        number_in_first_name_data,
                        number_in_lastname_name_data,
                        space_in_firstname_data, space_in_lastname_data,
                        missing_firstname_data, missing_lastname_data,
                        empty_firstname_data, empty_last_name_data)


class UserRegistrationTest(BaseTest):
    """Contains user registration test methods."""

    def test_user_should_register(self):
        """Create an account."""
        response = self.client.post(
            self.registration_url, valid_user_data, format="json")
        self.assertEqual(response.status_code, 201)

    def test_user_should_not_register_with_invalid_email(self):
        """Create an account with an invalid email."""
        response = self.client.post(
            self.registration_url, invalid_email_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(str(response.data["email"][0]),
                         "Enter a valid email address.")

    def test_user_should_not_register_with_a_taken_email(self):
        """Create an account with a taken email"""
        self.client.post(
            self.registration_url, valid_user_data, format="json")
        response = self.client.post(
            self.registration_url, valid_user_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(str(response.data["email"][0]),
                         "user with this email already exists.")

    def test_user_should_not_register_with_a_weak_password(self):
        """Create an account with a weak password."""
        response = self.client.post(
            self.registration_url, weak_password_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.data["password"])

    def test_user_should_not_register_with_a_name_with_a_number(self):
        """Create an account with a first name that has a number in it."""
        response = self.client.post(
            self.registration_url, number_in_first_name_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.data["first_name"])

    def test_user_should_not_register_with_a_lastname_with_a_number(self):
        """Create an account with a last name that has a number in it."""
        response = self.client.post(
            self.registration_url, number_in_lastname_name_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.data["last_name"])

    def test_user_should_not_register_with_a_lastname_with_a_space(self):
        """Create an account with a last name that has a space in it."""
        response = self.client.post(
            self.registration_url, space_in_lastname_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.data["last_name"])

    def test_user_should_not_register_with_first_name_with_a_space(self):
        """Create an account with a first name that has a space in it."""

        response = self.client.post(
            self.registration_url, space_in_firstname_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.data["first_name"])

    def test_user_should_not_register_with_unmatching_passwords(self):
        """Create an account with passwords that donot match."""
        response = self.client.post(
            self.registration_url, umatching_passwords_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.data["passwords"])

    def test_user_should_not_register_with_no_first_name(self):
        """Create an account with no firstname."""
        response = self.client.post(
            self.registration_url, missing_firstname_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.data["first_name"])

    def test_user_should_not_register_with_no_lastname(self):
        """Create an account with no lastname."""
        response = self.client.post(
            self.registration_url, missing_lastname_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.data["last_name"])

    def test_user_should_not_register_with_an_empty_lastname(self):
        """Create an account with an empty lastname."""
        response = self.client.post(
            self.registration_url, empty_last_name_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.data["last_name"])

    def test_user_should_not_register_with_an_empty_firstname(self):
        """Create an account with an empty firstname."""
        response = self.client.post(
            self.registration_url, empty_firstname_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.data["first_name"])
