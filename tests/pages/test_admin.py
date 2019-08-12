from django.contrib.admin.sites import AdminSite
from pages.models import Term
from pages.admin import PagesAdmin
from django.test import TestCase


class MockRequest(object):
    """
    Create A mock request object.

    Aminimal request consists of a Python object with a user attribute.
    """

    def __init__(self, user=None):
        self.user = user


class AdminTest(TestCase):
    """
    Checks if the admin cannot perform restricted actions.

    Admins should not be able to delete or add new terms instances
    They should only update the terms and conditions
    """

    def setUp(self):
        """Create a reusable model admin instance."""
        self.model_admin = PagesAdmin(model=Term, admin_site=AdminSite())

    def test_should_not_add_new_term_instances(self):
        """Test that users cannot add new terms instances."""
        self.assertEquals(
            self.model_admin.has_add_permission(MockRequest), False)

    def test_should_not_delete_default_term_instance(self):
        """Test that users cannot delete the existing terms of service."""
        self.assertEquals(self.
                          model_admin.has_delete_permission(MockRequest),
                          False)
