from django.test import TestCase

from tests.factories.authentication_factory import UserFactory
from authentication.models import User


class BaseAbstractModelTest(TestCase):
    """This class contains tests for the base abstract model"""

    def setUp(self):
        self.user1 = UserFactory.create(first_name='Test')

    def test_that_soft_delete_works(self):
        self.user1.soft_delete()
        soft_deleted_user = User.objects.filter(
            is_deleted=True, first_name='Test')
        self.assertTrue(soft_deleted_user)
