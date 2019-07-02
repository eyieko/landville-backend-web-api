import json

from rest_framework import serializers
import re
import pytz
import datetime
from django.core.validators import ValidationError

from property.models import Property, BuyerPropertyList, PropertyEnquiry

from property.validators import (
    validate_address, validate_coordinates, validate_image_list, validate_visit_date)
from utils.media_handlers import CloudinaryResourceHandler


class PropertySerializer(serializers.ModelSerializer):
    """This class handles serializing and
       deserializing of Property objects"""

    price = serializers.FloatField()
    lot_size = serializers.FloatField()
    image_others = serializers.ListField(
        required=False, validators=[validate_image_list])
    address = serializers.JSONField(validators=[validate_address])
    coordinates = serializers.JSONField(validators=[validate_coordinates])

    class Meta:
        model = Property
        exclude = ('is_deleted',)
        read_only_fields = ('view_count', 'slug', 'is_deleted',
                            'is_published', 'is_sold', 'sold_at', 'list_date')

    def update(self, instance, validated_data):
        """
        Define how images and videos are updated and deleted. All other fields
        are updated the default way.
        All new images are appended to the list of images in the database.
        """
        # Ensure that read-only fields cannot be updated by the user
        for key, value in validated_data.copy().items():
            if key in self.Meta.read_only_fields:
                validated_data.pop(key)

        # Update the list of images in the database if any image is passed.

        if instance.image_others:
            images_in_DB = instance.image_others.copy()
        else:
            images_in_DB = []

        updated_image_list = validated_data.pop('image_others', None)

        if updated_image_list:
            for image in updated_image_list:
                images_in_DB.append(image)
        instance.image_others = images_in_DB

        # Update the main image if it is passed. We won't delete
        # the older image. It is instead added to the `image_others`
        updated_main_image = validated_data.pop('image_main', None)
        if updated_main_image:
            current_main_image = instance.image_main
            instance.image_main = updated_main_image[0]
            instance.image_others.append(current_main_image)

        # update video
        if instance.video:
            video_in_DB = instance.video
        else:
            video_in_DB = None

        updated_video = validated_data.pop('video', None)

        if updated_video:
            # The old video is replaced
            video_in_DB = updated_video[0]
            instance.video = video_in_DB

        # we need to ensure that coordinates and addresses are decoded
        # before they can be saved
        coordinates = validated_data.pop('coordinates', None)
        if isinstance(coordinates, str):
            validated_data['coordinates'] = json.loads(coordinates)

        address = validated_data.pop('address', None)
        if isinstance(address, str):
            validated_data['address'] = json.loads(address)

        instance.save()
        return super().update(instance, validated_data)


class BuyerPropertyListSerializer(serializers.ModelSerializer):
    """
    Class handling serialization and deserialization
    of BuyerPropertyList objects.
    """

    property_of_interest = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = BuyerPropertyList
        exclude = ('created_at', 'updated_at', 'is_deleted', 'id')


class PropertyEnquirySerializer(serializers.ModelSerializer):
    """ serializer class for property Enquiry """
    visit_date = serializers.DateTimeField(validators=[validate_visit_date])

    class Meta:
        model = PropertyEnquiry
        fields = ['enquiry_id', 'visit_date', 'message']

    def update(self, instance, validated_data):
        """ update an existing enquiry """

        instance.message = validated_data.get('message', instance.message)
        instance.visit_date = validated_data.get(
            'visit_date', instance.visit_date)

        instance.save()
        return instance
