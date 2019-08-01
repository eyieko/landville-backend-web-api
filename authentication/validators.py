import re
from rest_framework import serializers


def validate_phone_number(phone):
    """Validate the phone number to match expected format"""
    p = re.compile(r'\+?\d{3}\s?\d{3}\s?\d{7}')
    q = re.compile(r'^.{10,16}$')
    if not (p.match(phone) and q.match(phone)):
        raise serializers.ValidationError(
            "Phone number must be of the format +234 123 4567890"
        )
