import os
from datetime import (
    datetime,
    timedelta,
)

import jwt
from django.conf import settings
from rest_framework import exceptions

from authentication.models import (
    PasswordResetToken,
    User,
)
from utils.tasks import send_email_notification


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

        payload = {
            "subject": "Reset your LandVille Password",
            "recipient": [to_email],
            "text_body": "",
            "html_body": "password_reset.html",
            "context": {
                'token': token,
                'domain': domain
            }
        }
        send_email_notification.delay(payload)
