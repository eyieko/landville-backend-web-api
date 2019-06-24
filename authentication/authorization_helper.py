from datetime import (
    datetime,
    timedelta,
)

import jwt
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from authentication.models import User


def generate_validation_url(data, user_id=None):
    """Send out a verification email."""
    if not user_id:
        user_id = User.objects.filter(email=data[1]).first().id
    email = data[1] if len(data) > 1 else User.objects.filter(
        id=user_id).first().email
    encoded_jwt = jwt.encode(
        {
            "email": email,
            "exp": datetime.utcnow() +
                   timedelta(hours=23)
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    ).decode("utf-8")
    url = f"http://{get_current_site(data[0]).domain}/api/v1/" \
        f"auth/verify/?token={encoded_jwt}~{user_id}"

    return url
