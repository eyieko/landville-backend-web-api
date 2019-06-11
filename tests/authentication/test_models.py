from django.test import TestCase, TransactionTestCase

from authentication.models import User, UserProfile
from tests.factories.authentication_factory import UserFactory, UserProfileFactory, ClientFactory
from authentication.models import Client


class UserManagerTest(TransactionTestCase):
    """This class will contain all tests on the custom User manager"""

    def setUp(self):
        self.user1 = UserFactory.create(email='user@email.com')
        self.user2 = User.objects.create_user(
            first_name='Test', last_name='User', email='test@mail.com', password='password', role='CA')

    def test_that_the_string_representation_is_correct(self):
        self.assertEqual(str(self.user1), 'user@email.com')

    def test_client_admin_is_created(self):
        self.assertEqual(self.user2.is_active, True)

    def test_email_representation(self):
        self.assertIn('user', self.user1.get_email)
        self.assertIn('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9', self.user1.token)

    def test_that_user_token_is_created(self):
        self.assertIsNotNone(self.user2.token)

    def test_that_user_cannot_be_created_without_password(self):
        with self.assertRaises(TypeError) as e:
            User.objects.create_user(
                first_name='Test', last_name='User', email='test_user@mail.com', password='')
        self.assertEqual(str(e.exception), 'Users must have a password.')

    def test_that_user_cannot_be_created_without_first_name(self):
        with self.assertRaises(TypeError) as e:
            User.objects.create_user(
                first_name='', last_name='User', email='test@email.com', password='password')
        self.assertEqual(str(e.exception), 'Users must have a first name.')

    def test_that_user_cannot_be_created_without_last_name(self):
        with self.assertRaises(TypeError) as e:
            User.objects.create_user(
                first_name='Test', last_name='', email='test@mail.com', password='password')
        self.assertEqual(str(e.exception), 'Users must have a last name.')

    def test_that_user_cannot_be_created_without_email_address(self):
        with self.assertRaises(TypeError) as e:
            User.objects.create_user(
                first_name='Test', last_name='User', email='', password='password')
        self.assertEqual(str(e.exception), 'Users must have an email address.')

    def test_that_we_can_successfully_create_user(self):
        user = User.objects.create_user(
            first_name='Test', last_name='User', email='test5@mail.com', password='password', role="BY")
        self.assertTrue(user.is_active)
        self.assertIsInstance(self.user2, User)
        self.assertIsInstance(self.user1, User)

    def test_that_superuser_cannot_be_created_without_email_address(self):
        with self.assertRaises(TypeError) as e:
            User.objects.create_superuser(
                first_name='Super', last_name='User', email='', password='password')
        self.assertEqual(str(e.exception),
                         'Superusers must have an email address.')

    def test_that_superuser_cannot_be_created_without_first_name(self):
        with self.assertRaises(TypeError) as e:
            User.objects.create_superuser(
                first_name='', last_name='User', email='superuser@mail.com', password='password')
        self.assertEqual(str(e.exception),
                         'Superusers must have a first name.')

    def test_that_superuser_cannot_be_created_without_last_name(self):
        with self.assertRaises(TypeError) as e:
            User.objects.create_superuser(
                first_name='Super', last_name=None, email='superuser@mail.com', password='password')
        self.assertEqual(str(e.exception),
                         'Superusers must have a last name.')

    def test_that_superuser_cannot_be_created_without_password(self):
        with self.assertRaises(TypeError) as e:
            User.objects.create_superuser(
                first_name='Super', last_name='User', email='superuser@mail.com', password='')
        self.assertEqual(str(e.exception),
                         'Superusers must have a password.')

    def test_that_we_can_create_superuser(self):
        User.objects.create_superuser(
            'Super', 'User', 'superuser@mail.com', 'password')
        superuser = User.objects.filter(is_superuser=True).first()
        self.assertEqual('superuser@mail.com', str(superuser))
        self.assertTrue(superuser.is_superuser)
        self.assertIsInstance(superuser, User)


class UserProfileModelTest(TestCase):
    """Test the UserProfile model"""

    def setUp(self):
        self.user1 = UserFactory.create(email='user@email.com')
        self.profile1 = UserProfile.objects.get(user=self.user1)

    def test_that_the_string_representation_is_correct_for_a_profile_model(self):
        self.assertEqual(str(self.profile1), "user@email.com's Profile")

    def test_that_user_profile_relationship_is_accurate(self):
        self.assertEqual(self.user1.userprofile, self.profile1)


class ClientModelTest(TestCase):
    """Test the Client model"""

    def setUp(self):
        self.user1 = UserFactory.create()
        self.client1 = ClientFactory.create(client_admin=self.user1)

    def test_that_string_representation_for_client_model_is_correct(self):
        self.assertEqual(str(self.client1), self.client1.client_name)

    def test_should_update_client_approval_status(self):
        """Test approval status can be updated successfully."""
        self.client1.approval_status = 'rejected'
        self.client1.save()
        approval_status = Client.objects.get(
            email=self.client1.email).approval_status
        self.assertEqual(approval_status, "rejected")
