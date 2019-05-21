from django.test import TestCase, TransactionTestCase

from authentication.models import User
from tests.factories.authentication_factory import UserFactory, UserProfileFactory, ClientFactory


class UserManagerTest(TransactionTestCase):
    """This class will contain all tests on the custom User manager"""

    def setUp(self):
        self.user1 = UserFactory.create(first_name='User', last_name='One')

    def test_that_the_string_representation_is_correct(self):
        self.assertEqual(str(self.user1), 'User One')

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
        self.assertEqual('Super User', str(superuser))
        self.assertTrue(superuser.is_superuser)
        self.assertIsInstance(superuser, User)


class UserProfileModelTest(TestCase):
    """Test the UserProfile model"""

    def setUp(self):
        self.user1 = UserFactory.create(first_name='User', last_name='One')
        self.profile1 = UserProfileFactory.create(user=self.user1)

    def test_that_the_string_representation_is_correct_for_a_profile_model(self):
        self.assertEqual(str(self.profile1), "User One's Profile")

    def test_that_user_profile_relationship_is_accurate(self):
        self.assertEquals(self.user1.userprofile, self.profile1)


class ClientModelTest(TestCase):
    """Test the Client model"""

    def setUp(self):
        self.user1 = UserFactory.create()
        self.client1 = ClientFactory.create(client_admin=self.user1)

    def test_that_string_representation_for_client_model_is_correct(self):
        self.assertEqual(str(self.client1), self.client1.client_name)
