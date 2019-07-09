from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from authentication.models import User
from tests.factories.authentication_factory import UserFactory, ClientFactory


class BaseTest(APITestCase):
    """Set up the testing client."""

    def setUp(self):
        self.client = APIClient()
        self.registration_url = reverse("auth:register")
        self.client_url = reverse("auth:client")
        self.client_profile = reverse("auth:profile")
        self.login_url = reverse("auth:login")
        self.user = UserFactory.create()
        self.company = ClientFactory.create()

        self.new_user = {
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email + "m",
            "password": self.user.password,
            "confirmed_password": self.user.password,
            "role": self.user.role
        }

        self.client_with_invalid_address = {
            "client_name": self.company.client_name + "i",
            "phone": "+234 805 9544607",
            "client_admin": self.user.pk,
            "email": self.company.email + "i",
            "address": "address"
        }
        self.valid_client_data = {
            "client_name": self.company.client_name + "i",
            "phone": "+234 805 9544607",
            "client_admin": self.user.pk,
            "email": self.company.email + "i",
            "address": self.company.address
        }
        self.client_with_no_street = {
            "client_name": self.company.client_name + "i",
            "phone": "+234 805 9544607",
            "client_admin": self.user.pk,
            "email": self.company.email + "i",
            "address": {"State": "street", "City": "state"}
        }
        self.client_with_no_city = {
            "client_name": self.company.client_name + "i",
            "phone": "+234 805 9544607",
            "client_admin": self.user.pk,
            "email": self.company.email + "i",
            "address": {"State": "street", "Street": "state"}
        }
        self.client_with_no_state = {
            "client_name": self.company.client_name + "i",
            "phone": "+234 805 9544607",
            "client_admin": self.user.pk,
            "email": self.company.email + "i",
            "address": {"City": "street", "Street": "state"}
        }
        self.client_with_invalid_state = {
            "client_name": self.company.client_name + "i",
            "phone": "+234 805 9544607",
            "client_admin": self.user.pk,
            "email": self.company.email + "i",
            "address": {"City": "city", "State": 345678, "Street": "street"}
        }
        self.client_with_invalid_city = {
            "client_name": self.company.client_name + "i",
            "phone": "+234 805 9544607",
            "client_admin": self.user.pk,
            "email": self.company.email + "i",
            "address": {"City": 0.345678, "State": "street", "Street": "state"}
        }
        self.client_with_invalid_street = {
            "client_name": self.company.client_name + "i",
            "phone": "+234 805 9544607",
            "client_admin": self.user.pk,
            "email": self.company.email + "i",
            "address": {"City": "city", "State": "street", "Street": 345678}
        }
        self.client_with_empty_street = {
            "client_name": self.company.client_name + "i",
            "phone": "+234 805 9544607",
            "client_admin": self.user.pk,
            "email": self.company.email + "i",
            "address": {"City": "city", "State": "street", "Street": ""}
        }

        self.client_with_empty_city = {
            "client_name": self.company.client_name + "i",
            "phone": "+234 805 9544607",
            "client_admin": self.user.pk,
            "email": self.company.email + "i",
            "address": {"City": "", "State": "street", "Street": "street"}
        }

        self.client_with_empty_state = {
            "client_name": self.company.client_name + "i",
            "phone": "+234 805 9544607",
            "client_admin": self.user.pk,
            "email": self.company.email + "i",
            "address": {"City": "city", "State": "", "Street": "street"}
        }

        self.updated_profile_with_image = {
            "phone": "2347725678900",
            "address": '{"City": "Up state", "State": "New York", "Street": "Kigali"}',
            "user_level": "S",
            "image": None,
            "security_question": "What is the name of your favorite childhood friend",
            "security_answer": "Dave",
            "employer": "Andela Uganda",
            "designation": "DevOps Engineer",
            "next_of_kin": "mom",
            "next_of_kin_contact": "2347724065130",
            "bio": "I am a kind being"
        }

        self.updated_profile = {
            "phone": "2347725678900",
            "address": {"City": "Up state", "State": "New York", "Street": "Kigali"},
            "user_level": "S",
            "image": None,
            "security_question": "What is the name of your favorite childhood friend",
            "security_answer": "Dave",
            "employer": "Andela Uganda",
            "designation": "DevOps Engineer",
            "next_of_kin": "mom",
            "next_of_kin_contact": "2347724065130",
            "bio": "I am a kind being"
        }

        self.updated_profile_with_empty_city_field = {
            "phone": "2347725678900",
            "address": {"City": " ", "State": "New York", "Street": "Kigali"},
            "user_level": "S",
            "image": None,
            "security_question": "What is the name of your favorite childhood friend",
            "security_answer": "Dave",
            "employer": "Andela Uganda",
            "designation": "DevOps Engineer",
            "next_of_kin": "mom",
            "next_of_kin_contact": "2347724065130",
            "bio": "I am a kind being"
        }

        self.updated_profile_without_security_answer_field = {
            "phone": "2347725678900",
            "address": {"City": "Up state", "State": "New York", "Street": "Kigali"},
            "user_level": "S",
            "image": None,
            "security_question": "What is the name of your favorite childhood friend",
            "employer": "Andela Uganda",
            "designation": "DevOps Engineer",
            "next_of_kin": "mom",
            "next_of_kin_contact": "2347724065130",
            "bio": "I am a kind being"
        }

        self.updated_profile_without_next_of_kin_field = {
            "phone": "2347725678900",
            "address": {"City": "Up state", "State": "New York", "Street": "Kigali"},
            "user_level": "S",
            "image": None,
            "security_question": "What is the name of your favorite childhood friend",
            "security_answer": "Dave",
            "employer": "Andela Uganda",
            "designation": "DevOps Engineer",
            "next_of_kin_contact": "2347724065130",
            "bio": "I am a kind being"
        }

        self.updated_profile_without_phone_field = {
            "address": {"City": "Up state", "State": "New York", "Street": "Kigali"},
            "user_level": "S",
            "image": None,
            "security_question": "What is the name of your favorite childhood friend",
            "security_answer": "Dave",
            "employer": "Andela Uganda",
            "designation": "DevOps Engineer",
            "next_of_kin": "mom",
            "next_of_kin_contact": "2347724065130",
            "bio": "I am a kind being"
        }

        self.updated_profile_with_invalid_phonenumber = {
            "address": {"City": "Up state", "State": "New York", "Street": "Kigali"},
            "phone": "0774567809",
            "user_level": "S",
            "image": None,
            "security_question": "What is the name of your favorite childhood friend",
            "security_answer": "Dave",
            "employer": "Andela Uganda",
            "designation": "DevOps Engineer",
            "next_of_kin": "mom",
            "next_of_kin_contact": "2347724065130",
            "bio": "I am a kind being"
        }

        self.updated_profile_without_address_field = {
            "phone": "2347725678900",
            "user_level": "S",
            "image": None,
            "security_question": "What is the name of your favorite childhood friend",
            "security_answer": "Dave",
            "employer": "Andela Uganda",
            "designation": "DevOps Engineer",
            "next_of_kin": "mom",
            "next_of_kin_contact": "2347724065130",
            "bio": "I am a kind being"
        }

        self.updated_profile_without_employer_field = {
            "phone": "2347725678900",
            "address": '{"City": "Up state", "State": "New York", "Street": "Kigali"}',
            "user_level": "S",
            "image": None,
            "security_question": "What is the name of your favorite childhood friend",
            "security_answer": "Dave",
            "designation": "DevOps Engineer",
            "next_of_kin": "mom",
            "next_of_kin_contact": "2347724065130",
            "bio": "I am a kind being"
        }

        self.profile_with_image = {
            "phone": "2347725678900",
            "address": {"City": "Up state", "State": "New York", "Street": "Kigali"},
            "user_level": "STARTER",
            "image": 'http://res.cloudinary.com/landville/image/upload/v1561568984/xep5qlwc8.png',
            "security_question": "What is the name of your favorite childhood friend",
            "security_answer": "Dave",
            'employer': "Andela",
            "designation": "DevOps Engineer",
            "next_of_kin": "mom",
            "next_of_kin_contact": "2347724065130",
            "bio": "I am a kind being"
        }
