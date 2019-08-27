from django.test import TestCase
from django.urls import reverse
from rest_framework import authentication, exceptions
from datetime import datetime, timedelta
import jwt

from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory
from django.conf import settings

from authentication.models import User
from tests.factories.authentication_factory import UserFactory
from authentication.backends import JWTAuthentication


class JWTAuthenticationTest(TestCase):
    """Test the JWT Authentication implementation"""

    def setUp(self):
        self.user = UserFactory.create(first_name='User', last_name='One')
        self.user_token = self.user.token
        self.user.save()
        self.client = APIClient()
        self.jwt_auth = JWTAuthentication()
        self.factory = APIRequestFactory()
        self.token_expiry = datetime.now() - timedelta(hours=1)

        self.expired_token = jwt.encode({
            'id': self.user.id,
            'email': self.user.email,
            'exp': int(self.token_expiry.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

    def test_authentication_failure_because_header_is_None(self):
        """Test if authentication fails when a request has authorization
        headers with a length of 0"""
        request = self.factory.get('/')
        request.META['HTTP_AUTHORIZATION'] = ''
        res = self.jwt_auth.authenticate(request)
        self.assertEqual(res, None)

    def test_authentication_failure_because_header_length_is_1(self):
        """Test if authentication fails when a request has authorization
        headers with a length of 1"""
        request = self.factory.get('/')
        request.META['HTTP_AUTHORIZATION'] = 'length'
        res = self.jwt_auth.authenticate(request)
        self.assertEqual(res, None)

    def test_authentication_failure_if_header_length_is_greater_than_2(self):
        """Test if authentication fails when a request has authorization
        headers with a length greater than 2"""
        request = self.factory.get('/')
        request.META['HTTP_AUTHORIZATION'] = 'length is greater than 2'
        res = self.jwt_auth.authenticate(request)
        self.assertEqual(res, None)

    def test_authentication_success_if_prefixes_match(self):
        """We unit test our authentication method to see if the method
        returns `None` when the prefixes match"""
        request = self.factory.get('/')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer, {}'.format(
            self.user_token)
        res = self.jwt_auth.authenticate(request)
        self.assertEqual(res, None)

    def test_authentication_failure_if_prefixes_mismatch(self):
        """We unit test our authentication method to see if the method
        returns `None` when the prefixes mismatch"""
        request = self.factory.get('/')
        request.META['HTTP_AUTHORIZATION'] = 'dgdggdg, {}'.format(
            self.user_token)
        res = self.jwt_auth.authenticate(request)
        self.assertEqual(res, None)

    def test_authentication_success_if_valid_token(self):
        """We unit test our authentication method to see if the method
        success if coreect token provided"""
        request = self.factory.get('/')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer, {}'.format(
            self.user_token)
        res = self.jwt_auth._authenticate_credentials(request, self.user_token)

        self.assertEqual(self.user.email, res[0].email)

    def test_authentication_failure_incase_of_expired_token(self):
        """We unit test our authentication method to see if the method
        returns expired token error message when supplied with invalid token"""
        request = self.factory.get('/')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer, {}'.format(
            self.expired_token)
        with self.assertRaises(exceptions.AuthenticationFailed) as e:
            res = self.jwt_auth._authenticate_credentials(
                request, self.expired_token)
        self.assertEqual(
            str(e.exception),
            'Your token has expired, please log in again.'
        )

    def test_authentication_failure_incase_of_decoding_error(self):
        """We unit test our authentication method to see if the method
        returns decoding error when supplied with invalid"""
        request = self.factory.get('/')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer, {}'.format('fake-token')
        with self.assertRaises(exceptions.AuthenticationFailed) as e:
            res = self.jwt_auth._authenticate_credentials(
                request, 'fake-token')
        self.assertEqual(str(e.exception), 'Not enough segments')

    def test_authentication_failure_if_user_non_existent(self):
        """We unit test our authentication method to see if the method
        returns error message when supplied with a non existent user"""
        non_existing = User.objects.create_user(
            first_name='trial', last_name='trial2', email='trial@trial.com', password='triall')
        non_existing.delete()
        request = self.factory.get('/')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer, {}'.format(
            non_existing.token)
        with self.assertRaises(exceptions.AuthenticationFailed) as e:
            res = self.jwt_auth._authenticate_credentials(
                request, non_existing.token)
        self.assertEqual(
            str(e.exception), 'User matching this token was not found.'
        )

    def test_authentication_failure_if_user_not_active(self):
        """We unit test our authentication method to see if the method
        returns error message when supplied with an inactive user"""
        non_existing = User.objects.create_user(
            first_name='trial', last_name='trial2', email='trial@trial.com', password='triall')
        non_existing.is_active = False
        non_existing.save()
        request = self.factory.get('/')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer, {}'.format(
            non_existing.token)
        with self.assertRaises(exceptions.AuthenticationFailed) as e:
            res = self.jwt_auth._authenticate_credentials(
                request, non_existing.token)
        self.assertEqual(
            str(e.exception), 'Forbidden! This user has been deactivated.'
        )
