from datetime import datetime, timedelta
from urllib import parse
import os
import jwt
from django.conf import settings
from rest_framework import exceptions

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site

from authentication.models import User, PasswordResetToken


class ResetHandler:
    """
    This class contains the methods for creating and validating 
    tokens fr users upon requesting a reset link then send 
    them to users via email
    """

    def create_verification_token(self, payload):
        """
        Create a JWT token to be sent in the verification
        email url
        """

        if not isinstance(payload, dict):
            raise TypeError('Payload must be a dictionary!')

        token_expiry = datetime.now() + timedelta(hours=12)

    
        token = jwt.encode({
            'email': payload['email'],
            'exp': int(token_expiry.strftime('%s'))},
            settings.SECRET_KEY, algorithm='HS256')
        token = token.decode('utf-8')
        
        """
        here we store the encoded token in our database 
        under the PasswordResetToken model. To be used later 
        for verification
        """
        PasswordResetToken.objects.create(token=token)
        return token

    def validate_token(self, token):
        """
        Validate provided token. The email encoded in the token
        should be equal to the email of the user instance being
        passed.
        """

        try:
            decoded_token = jwt.decode(
                token, settings.SECRET_KEY, algorithm='HS256')

        except jwt.exceptions.ExpiredSignatureError:
            msg = 'Your token has expired. Make a new token and try again'
            raise exceptions.AuthenticationFailed(msg)

        except Exception:
            msg = 'Error. Could not decode token!'
            return msg
        
        try:
            user = User.objects.get(email=decoded_token.get('email'))
        except User.DoesNotExist:
            msg = 'User matching this token was not found.'
            raise exceptions.AuthenticationFailed(msg)

        return (decoded_token, user)

    def send_password_reset_link(self, to_email, token):
        domain = os.environ.get('DOMAIN')
        html_content = render_to_string('password_reset.html',
                                        {'token': token, 'domain': domain})
        subject = 'Reset your LandVille Password'
        from_email = settings.EMAIL_HOST_USER
        msg = EmailMessage(subject, html_content, from_email, [to_email])
        msg.content_subtype = 'html'
        msg.mixed_subtype = 'related'
        msg.send()
