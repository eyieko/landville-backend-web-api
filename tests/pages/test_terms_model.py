from django.test import TestCase
from pages.models import Term
from tests.pages.test_base import TermsTestBase


class TestModel(TermsTestBase):
    """Tests the Terms model."""

    def test_model_string_representation(self):
        """Test if the model picks the specified title."""
        self.assertEquals(str(self.terms), "Terms and Conditions")
