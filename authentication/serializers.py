from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class RegistrationSerializer(serializers.ModelSerializer):
    """Serialize registration requests and create a new user."""

    password = serializers.CharField(
        max_length=128,
        min_length=6,
        write_only=True,
        error_messages={
            "min_length": "Password should be atleast {min_length} characters"
        }
    )
    confirmed_password = serializers.CharField(
        max_length=128,
        min_length=6,
        write_only=True,
        error_messages={
            "min_length": "Password should be atleast {min_length} characters"
        }
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name",
                  "password", "confirmed_password"]
        validators = []

    def validate(self, data):
        """Validate data before it gets saved."""
        first_name = data.get("first_name", None)
        last_name = data.get("last_name", None)

        if first_name is None:
            raise serializers.ValidationError({
                "first_name": ("Firstname is required")
            })
        if first_name == "":
            raise serializers.ValidationError({
                "first_name": ("Firstname may not be blank")
            })

        if last_name is None:
            raise serializers.ValidationError({
                "last_name": ("Lastname is required")
            })
        if last_name == "":
            raise serializers.ValidationError({
                "last_name": ("Lastname may not be blank")
            })

        confirmed_password = data.get("confirmed_password", None)
        try:
            validate_password(data["password"])
        except ValidationError as identifier:
            raise serializers.ValidationError({
                "password": str(identifier).replace("["", "").replace(""]", "")})

        if not self.do_passwords_match(data["password"], confirmed_password):
            raise serializers.ValidationError({
                "passwords": ("Passwords do not match")
            })

        if self.has_numbers(first_name):
            raise serializers.ValidationError({
                "first_name": ("Firstname cannot contain numbers")
            })
        if self.has_numbers(last_name):
            raise serializers.ValidationError({
                "last_name": ("Lastname cannot contain numbers")
            })
        if self.has_spaces(first_name):
            raise serializers.ValidationError({
                "first_name": ("Firstname cannot contain spaces")
            })
        if self.has_spaces(last_name):
            raise serializers.ValidationError({
                "last_name": ("Lastname cannot contain spaces")
            })
        return data

    def create(self, validated_data):
        """Create a user."""
        del validated_data["confirmed_password"]
        return User.objects.create_user(**validated_data)

    def has_numbers(self, strval):
        """Check if a string contains a number."""
        return any(char.isdigit() for char in strval)

    def has_spaces(self, strval):
        """Check if a string contains a space."""
        return any(char.isspace() for char in strval)

    def do_passwords_match(self, password1, password2):
        """Check if passwords match."""
        return password1 == password2


class PasswordResetSerializer(serializers.Serializer):

    password = serializers.CharField(
        max_length=128,
        min_length=6,
        write_only=True,
        error_messages={
            "min_length": "Password should be atleast {min_length} characters"
        }
    )
    confirmed_password = serializers.CharField(
        max_length=128,
        min_length=6,
        write_only=True,
        error_messages={
            "min_length": "Password should be atleast {min_length} characters"
        }
    )
    email = serializers.EmailField()

    def validate(self, data):

        if not self.do_passwords_match(data["password"],
                                       data["confirmed_password"]):
            raise serializers.ValidationError({
                "passwords": ("Passwords do not match")
            })
        return data

    def create(self, validated_data):
        """update a users password"""
        del validated_data["confirmed_password"]
        user = User.objects.filter(email=validated_data.get('email')).first()

        if not user:
            raise serializers.ValidationError({
                "user": ("User with that email was not found")
            })

        user.set_password(validated_data['password'])
        user.save()
        return user

    def do_passwords_match(self, password1, password2):
        """Check if passwords match."""
        return password1 == password2
