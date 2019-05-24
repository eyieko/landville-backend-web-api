from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
import jwt
from django.conf import settings
from datetime import datetime, timedelta
from .models import User


class EmailHelper:
    """A handy class to send emails."""
    @staticmethod
    def send_verification_email(data, user_id=None):
        """Send out a verification email."""
        if not user_id:
            user_id = User.objects.filter(email=data[1]).first().id
        email = data[1] if len(data) > 1 else User.objects.filter(
            id=user_id).first().email
        encoded_jwt = jwt.encode(
            {"email": email, "exp": datetime.utcnow() +
             timedelta(hours=23)},
            settings.SECRET_KEY,
            algorithm="HS256",
        ).decode("utf-8")
        url = f"http://{get_current_site(data[0]).domain}/auth/verify/?token={encoded_jwt}~{user_id}"
        subject = "Account Activation"
        body = f"Hello,\nYou are receiving this e-mail because you have created an account on LandVille, \nClick the link below to activate your account.\n\n{url}"
        EmailMessage(subject, body, to=[email]).send(fail_silently=False)
