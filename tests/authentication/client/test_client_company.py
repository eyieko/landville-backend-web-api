"""User registration tests."""
from tests.authentication.client.test_base import BaseTest
from rest_framework import status
from tests.utils.utils import TestUtils


class ClientCompanyTest(TestUtils):
    """Contains user registration test methods."""

    def test_create_client_company_with_invalid_phone_number(self):
        """
        Create a client company account with invalid phone number.
        """
        self.set_token()
        self.valid_client_data["phone"] = "345"
        response = self.client.post(
            self.client_url, self.valid_client_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Phone number must be of the format +234 123 4567890",
            str(response.data)
        )

    def test_create_client_company_with_invalid_address(self):
        """
        Create a client company account with invalid address.
        """
        self.set_token()
        self.valid_client_data["address"] = "address"
        response = self.client.post(
            self.client_url, self.client_with_invalid_address, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Company address should contain State, City and Street details",
            str(response.data)
        )

    def test_create_client_company_with_address_with_no_street(self):
        """
        Create a client company account with no street.
        """
        self.set_token()
        response = self.client.post(
            self.client_url, self.client_with_no_street, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Street is required in address", str(response.data))

    def test_create_client_company_with_address_with_no_city(self):
        """
        Create a client company account with no city.
        """
        self.set_token()
        response = self.client.post(
            self.client_url, self.client_with_no_city, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("City is required in address", str(response.data))

    def test_create_client_company_with_address_with_no_state(self):
        """
        Create a client company account with no state.
        """
        self.set_token()
        response = self.client.post(
            self.client_url, self.client_with_no_state, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("State is required in address", str(response.data))

    def test_create_client_company_with_address_with_invalid_state(self):
        """
        Create a client company account with invalid state.
        """
        self.set_token()
        response = self.client.post(
            self.client_url, self.client_with_invalid_state, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("State must be a string", str(response.data))

    def test_create_client_company_with_address_with_invalid_city(self):
        """
        Create a client company account with invalid city.
        """
        self.set_token()
        response = self.client.post(
            self.client_url, self.client_with_invalid_city, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("City must be a string", str(response.data))

    def test_create_client_company_with_address_with_invalid_street(self):
        """
        Create a client company account with invalid street.
        """
        self.set_token()
        response = self.client.post(
            self.client_url, self.client_with_invalid_street, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Street must be a string", str(response.data))

    def test_user_should_create_a_client_company(self):
        """Create a client company account."""
        self.set_token()
        response = self.client.post(
            self.client_url, self.valid_client_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_should_not_create_a_second_client_company(self):
        """
        Client admin should not create a second company account.
        """
        self.set_token()
        self.client.post(
            self.client_url, self.valid_client_data, format="json")
        response = self.client.post(
            self.client_url, self.valid_client_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(
            "You cannot be admin of more than one client client",
            str(response.data)
        )

    def test_get_client_company_with_no_company(self):
        """Retrieve company when no company is created"""
        self.set_token()
        response = self.client.get(
            self.client_url, format="json")
        self.assertIn("You don't have a client company created",
                      str(response.data))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_client_company(self):
        """Get client a company account."""
        self.set_token()
        self.client.post(
            self.client_url, self.valid_client_data, format="json")
        response = self.client.get(
            self.client_url, format="json")
        self.assertIn("You have retrieved your client company",
                      str(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_client_company_with_address_with_empty_street(self):
        """
        Create a client company account with no street.
        """
        self.set_token()
        response = self.client.post(
            self.client_url, self.client_with_empty_street, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Street value can not be empty", str(response.data))

    def test_create_client_company_with_address_with_empty_city(self):
        """
        Create a client company account with no street.
        """
        self.set_token()
        response = self.client.post(
            self.client_url, self.client_with_empty_city, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("City value can not be empty", str(response.data))

    def test_create_client_company_with_address_with_empty_state(self):
        """
        Create a client company account with no street.
        """
        self.set_token()
        response = self.client.post(
            self.client_url, self.client_with_empty_state, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("State value can not be empty", str(response.data))
