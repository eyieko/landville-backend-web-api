
from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from authentication.models import User
from tests.factories.authentication_factory import UserFactory


class BaseTest(APITestCase):
    """Set up the testing client."""

    def setUp(self):
        self.client = APIClient()
        self.registration_url = reverse("auth:register")
        self.verify_url = reverse("auth:verify")
        self.login_url = reverse("auth:login")
        self.user = UserFactory.create()

        self.new_user = {
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email+"m",
            "password": self.user.password,
            "confirmed_password": self.user.password,
            "role": self.user.role
        }

        self.umatching_passwords_data = {
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email+"s",
            "password": self.user.password,
            "confirmed_password": self.user.password+"v",
            "role": self.user.role
        }
        self.invalid_email_data = {
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email.replace("@", ""),
            "password": self.user.password,
            "confirmed_password": self.user.password,
            "role": self.user.role
        }
        self.invalid_role_data = {
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email+"p",
            "password": self.user.password,
            "confirmed_password": self.user.password,
            "role": "role"
        }
        self.no_role_field_data = {
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email+"p",
            "password": self.user.password,
            "confirmed_password": self.user.password
        }

        self.weak_password_data = {
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email+"m",
            "password": "123456",
            "confirmed_password": self.user.password,
            "role": self.user.role
        }
        self.number_in_first_name_data = {
            "first_name": self.user.first_name+"5",
            "last_name": self.user.last_name,
            "email": self.user.email+"s",
            "password": self.user.password,
            "confirmed_password": self.user.password,
            "role": self.user.role
        }
        self.number_in_lastname_name_data = {
            "first_name": self.user.first_name,
            "last_name": self.user.last_name+"5",
            "email": self.user.email+"s",
            "password": self.user.password,
            "confirmed_password": self.user.password,
            "role": self.user.role
        }
        self.space_in_lastname_data = {
            "first_name": self.user.first_name,
            "last_name": self.user.last_name+" s",
            "email": self.user.email+"s",
            "password": self.user.password,
            "confirmed_password": self.user.password,
            "role": self.user.role
        }

        self.space_in_firstname_data = {
            "first_name": self.user.first_name+" s",
            "last_name": self.user.last_name,
            "email": self.user.email+"s",
            "password": self.user.password,
            "confirmed_password": self.user.password,
            "role": self.user.role
        }

        self.missing_firstname_data = {
            "last_name": self.user.last_name,
            "email": self.user.email+"s",
            "password": self.user.password,
            "confirmed_password": self.user.password,
            "role": self.user.role
        }

        self.missing_lastname_data = {
            "first_name": self.user.first_name,
            "email": self.user.email+"s",
            "password": self.user.password,
            "confirmed_password": self.user.password,
            "role": self.user.role
        }
        self.empty_firstname_data = {
            "first_name": "",
            "last_name": self.user.last_name,
            "email": self.user.email+"s",
            "password": self.user.password,
            "confirmed_password": self.user.password,
            "role": self.user.role
        }

        self.empty_last_name_data = {
            "first_name": self.user.first_name,
            "last_name": "",
            "email": self.user.email+"s",
            "password": self.user.password,
            "confirmed_password": self.user.password,
            "role": self.user.role
        }
