from django.test import TestCase
from authentication.admin import UserCreationForm, UserChangeForm
from django import forms
from tests.authentication.admin.test_base import BaseTest


class FormTests(BaseTest):
    """Test custom user creation and change forms for in admin panel."""

    def test_user_creation_valid_form_data(self):
        """Test a user submits a valid form."""
        form = UserCreationForm(data=self.valid_user_data)
        form.save()
        self.assertTrue(form.is_valid())

    def test_user_creation_invalid_form_data(self):
        """Test a user submits an invalid form."""
        form = UserCreationForm(data=self.invalid_user_data)
        self.assertFalse(form.is_valid())
        self.assertRaises(forms.ValidationError)

    def test_user_change_form(self):
        """Test a user submits form with invalid confirm password"""
        form = UserCreationForm(data=self.invalid_user_data_2)
        self.assertFalse(form.is_valid())
        self.assertRaises(forms.ValidationError)
