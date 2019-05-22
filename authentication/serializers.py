from random import randint
from .models import User
from rest_framework import serializers
from .socialvalidators import SocialValidation


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
        :params access_token:
        :rturn : user_token
        """

        id_info = SocialValidation.google_auth_validation(
            access_token=access_token)

        # check if data data retrieved once token decoded is empty
        if id_info is None:
            raise serializers.ValidationError('token is not valid')

        # check if a user exists after decoding the token in the payload
        # the user_id confirms user existence since its a unique identifier

        if 'sub' not in id_info:
            raise serializers.ValidationError(
                'Token has expired or is invalid.Get another one ASAP')

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
            'password': randint(1000000, 200000000000)
        }

        new_user = User.objects.create_user(**payload)
        new_user.is_verified = True
        new_user.is_active = True
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
        :param access_token:
        :return: user_token
        """
        id_info = SocialValidation.facebook_auth_validation(
            access_token=access_token)

        # checks if the data retrieved once token is decoded is empty.
        if id_info is None:
            raise serializers.ValidationError('Token is not valid.')

        # Checks to see if there is a user id associated with the payload after decoding the token
        # this user_id confirms that the user exists on twitter because its a unique identifier.
        if 'id' not in id_info:
            raise serializers.ValidationError(
                'Token is not valid or has expired. Please get a new one.')

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
            'password': randint(1000000, 200000000000)
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
        :param data:
        :return: user_token
        """
        id_info = SocialValidation.twitter_auth_validation(access_token=data.get('access_token'),
                                                           access_token_secret=data.get('access_token_secret'))
        # Check if there is an error message in the id_info validation body
        if 'errors' in id_info:
            raise serializers.ValidationError(
                id_info.get('errors')[0]['message'])

        # checks if the data retrieved once token is decoded is empty.
        if id_info is None:
            raise serializers.ValidationError('Token is not valid.')

        # Checks to see if there is a user id associated with the payload after decoding the token
        # this user_id confirms that the user exists on twitter because its a unique identifier.
        if 'id_str' not in id_info:
            raise serializers.ValidationError(
                'Token is not valid or has expired. Please get a new one.')

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
            'password': randint(1000000, 200000000000)
        }

        try:
            new_user = User.objects.create_user(**payload)
            new_user.is_verified = True
            new_user.social_id = user_id
            new_user.save()
        except:
            raise serializers.ValidationError('Error While creating User.')

        return {"token": new_user.token}
