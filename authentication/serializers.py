import re
from authentication.models import User, Client
from rest_framework import serializers
from authentication.models import User, PasswordResetToken
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.exceptions import NotAuthenticated
from authentication.socialvalidators import SocialValidation
from utils.password_generator import randomStringwithDigitsAndSymbols
from django.contrib.auth import authenticate
from utils import BaseUtils
from utils.resethandler import ResetHandler


class RegistrationSerializer(serializers.ModelSerializer):
    """Serialize registration requests and create a new user."""

    password = serializers.CharField(
        max_length=128,
        min_length=6,
        write_only=True,
        error_messages={
            "min_length": "Password should be at least {min_length} characters"
        }
    )
    confirmed_password = serializers.CharField(
        max_length=128,
        min_length=6,
        write_only=True,
        error_messages={
            "min_length": "Password should be at least {min_length} characters"
        }
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name",
                  "password", "confirmed_password", "role"]
        validators = []

    def validate(self, data):
        """Validate data before it gets saved."""
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        role = data.get("role")

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

        if role is None:
            raise serializers.ValidationError({
                "role": ("Role is required")
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


class GoogleAuthSerializer(serializers.ModelSerializer):
    """
    Handle serialization and deserialization of User objects
    """

    access_token = serializers.CharField()

    class Meta:
        model = User
        fields = ['access_token']

    @staticmethod
    def validate_access_token(access_token):
        """
        Handles validating a request and decoding and getting user's info
        associated to an account on Google then authenticates the User
        : params access_token:
        : rturn: user_token
        """

        id_info = SocialValidation.google_auth_validation(
            access_token=access_token)

        # check if data data retrieved once token decoded is empty
        if id_info is None:
            raise serializers.ValidationError('token is not valid')

        # check if a user exists after decoding the token in the payload
        # the user_id confirms user existence since its a unique identifier

        user_id = id_info['sub']

        # query database to check if a user with the same email exists
        user = User.objects.filter(email=id_info.get('email'))

        # if the user exists,return the user token
        if user:
            return user[0].token

        # create a new user if no new user exists
        first_and_second_name = id_info.get('name').split()
        first_name = first_and_second_name[0]
        second_name = first_and_second_name[1]
        payload = {
            'email': id_info.get('email'),
            'first_name': first_name,
            'last_name': second_name,
            'password': randomStringwithDigitsAndSymbols()
        }

        new_user = User.objects.create_user(**payload)
        new_user.is_verified = True
        new_user.is_active = False
        new_user.social_id = user_id
        new_user.save()

        return new_user.token


class FacebookAuthAPISerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    access_token = serializers.CharField()

    class Meta:
        model = User
        fields = ['access_token']

    @staticmethod
    def validate_access_token(access_token):
        """
        Handles validating the request token by decoding and getting user_info associated
        To an account on facebook.
        Then authenticate the user.
        : param access_token:
        : return: user_token
        """
        id_info = SocialValidation.facebook_auth_validation(
            access_token=access_token)

        # checks if the data retrieved once token is decoded is empty.
        if id_info is None:
            raise serializers.ValidationError('Token is not valid.')

        # Checks to see if there is a user id associated with the payload after decoding the token
        # this user_id confirms that the user exists on twitter because its a unique identifier.

        user_id = id_info['id']

        # Query database to check if there is an existing user with the save email.
        user = User.objects.filter(email=id_info.get('email'))

        # Returns the user token showing that the user has been registered before and existing in our database.
        if user:
            return user[0].token

        # Creates a new user because email is not associated with any existing account in our app
        first_and_second_name = id_info.get('name').split()
        first_name = first_and_second_name[0]
        second_name = first_and_second_name[1]
        payload = {
            'email': id_info.get('email'),
            'first_name': first_name,
            'last_name': second_name,
            'password': randomStringwithDigitsAndSymbols()
        }

        new_user = User.objects.create_user(**payload)
        new_user.is_verified = True
        new_user.social_id = user_id
        new_user.save()

        return new_user.token


class TwitterAuthAPISerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    access_token = serializers.CharField()
    access_token_secret = serializers.CharField()

    class Meta:
        model = User
        fields = ['access_token', 'access_token_secret']

    def validate(self, data):
        """
        Handles validating the request token by decoding and getting user_info associated
        To an account on twitter.
        Then authenticate the user.
        : param data:
        : return: user_token
        """
        id_info = SocialValidation.twitter_auth_validation(access_token=data.get('access_token'),
                                                           access_token_secret=data.get('access_token_secret'))
        # Check if there is an error message in the id_info validation body
        if 'errors' in id_info:
            raise serializers.ValidationError(
                id_info.get('errors')[0]['message'])

        # Checks to see if there is a user id associated with the payload after decoding the token
        # this user_id confirms that the user exists on twitter because its a unique identifier.

        user_id = id_info['id_str']

        # Query database to check if there is an existing user with the save email.
        user = User.objects.filter(email=id_info.get('email'))

        # Returns the user token showing that the user has been registered before and existing in our database.
        if user:
            return {"token": user[0].token}

        # Creates a new user because email is not associated with any existing account in our app
        first_and_second_name = id_info.get('name').split()
        first_name = first_and_second_name[0]
        second_name = first_and_second_name[1]
        payload = {
            'email': id_info.get('email'),
            'first_name': first_name,
            'last_name': second_name,
            'password': randomStringwithDigitsAndSymbols()
        }

        try:
            new_user = User.objects.create_user(**payload)
            new_user.is_verified = True
            new_user.social_id = user_id
            new_user.save()
        except:
            raise serializers.ValidationError('Error While creating User.')

        return {"token": new_user.token}


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        max_length=128, min_length=6, write_only=True,)
    token = serializers.CharField(read_only=True)

    def validate(self, data):
        email = data.get("email", None)
        password = data.get("password", None)
        user = authenticate(username=email, password=password)

        if user is None:
            raise NotAuthenticated({
                "invalid": "invalid email and password combination"
            })
        if not user.is_verified:
            raise NotAuthenticated({
                "user": "Your email is not verified,please vist your mail box"
            })
        user = {
            "email": user.email,
            "token": user.token
        }
        return user


class ClientSerializer(serializers.ModelSerializer, BaseUtils):
    class Meta:
        model = Client
        fields = ['client_name', 'phone', 'email', 'address', 'client_admin']
        read_only_fields = ('is_deleted', 'is_published')

    def validate(self, data):
        """Validate data before it gets saved."""
        phone = data.get("phone")
        address = data.get("address")
        p = re.compile(r'\+?\d{3}\s?\d{3}\s?\d{7}')
        q = re.compile(r'^.{10,16}$')

        if not (p.match(phone) and q.match(phone)):
            raise serializers.ValidationError({
                "phone": "Phone number must be of the format +234 123 4567890"
            })

        #Validate the type of address
        self.validate_data_instance(address, dict, {"address": "Company address should contain State, City and Street details"})

        keys = ["State", "Street", "City"]
        for key in keys:

            self.validate_dictionary_keys(key, address, {
                "address": "{} is required in address".format(key)
                })
                
            self.validate_data_instance(address[key], str, {
                "address": "{} must be a string".format(key)
                })
            self.validate_empty_input(key, address, {
                "address":"{} value can not be empty".format(key)
                })

        return data


class PasswordResetSerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of email
     where password reset link will be sent."""
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['email']
        extra_kwargs = {
            'email': {
                'read_only': True
            }
        }
    
    def validate(self, data):
        """ validate user input. """
        email = data.get('email')
        message = 'If you have an account with us we have sent an email to reset your password'
        reset_handler = ResetHandler()

        try:
            User.objects.get(email=email)
            payload = {
                'email': email
            }
            token = reset_handler.create_verification_token(payload)
            reset_handler.send_password_reset_link(
                email, token)
            return {'message': message}
        
        except User.DoesNotExist:
            """
            we dont let the user know if the email requesting a reset
            link exists in our database. This prevents knowledge
            of which emails actually exist.
            """
            message = 'If you have an account with us we have sent an email to reset your password'
            return {'message': message}


class ChangePasswordSerializer(serializers.ModelSerializer):

    """Serialize actual changing of user password. """
    password = serializers.CharField(
        max_length=128,
        min_length=6,
        write_only=True,
        error_messages={
            "min_length": "Password should be at least {min_length} characters"
        }
    )
    confirm_password = serializers.CharField(
        max_length=128,
        min_length=6,
        write_only=True,
        error_messages={
            "min_length": "Password should be at least {min_length} characters"
        }
    )
    token = serializers.CharField()
    class Meta:
        model = PasswordResetToken
        fields = '__all__'


    def validate(self, data):
        """ Validate token, password and confirm password passed to this serializer """
        token = data.get('token')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        try:
            """ we try to see if the token exists in our database """
            user_token = PasswordResetToken.objects.get(token=token)
            """ we then check is it is valid """
            if not user_token.is_valid:
                raise serializers.ValidationError({
                "token" : "This token is no longer valid, please get a new one"
            })
    
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError({
                "token" : "We couldn't find such token in our database"
            })
        
        result = ResetHandler().validate_token(user_token.token)
        """ 
        If the result is a tuple, it means decoding and  verification was successfull,
        we proceed with the process, else, raise another validation error.
        """
        if type(result) == tuple:
            
            if not RegistrationSerializer().do_passwords_match(password, confirm_password):
                """ 
                check if password and confirm passwords do match.
                no need to create another function since we already have one inside our RegistrationSerializer
                class above
                 """
                raise serializers.ValidationError({
                "error" : "passwords do not match"
            })
            try:
                validate_password(data["password"])
            except ValidationError as identifier:
                raise serializers.ValidationError({
                    "password": identifier.messages[0]
                })
            user = result[1]
            user.set_password(password)
            user.save()
            user_token.is_valid = False
            user_token.save()

        else:
            """we raise an exception with the incoming error. """
            raise serializers.ValidationError({
                "token" : result
            })
        
        return {"message": "password has been changed successfully"}
