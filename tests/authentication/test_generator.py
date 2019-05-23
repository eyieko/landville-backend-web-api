from utils.password_generator import randomStringwithDigitsAndSymbols
from django.test import TestCase


class TestPassWordGenerator(TestCase):
    def test_password_with_length_twenty(self):
        result = randomStringwithDigitsAndSymbols()
        self.assertEqual(len(result), 20)
