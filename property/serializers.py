from rest_framework import serializers

from property.models import Property
from property.validators import validate_address, validate_coordinates, validate_image_list


class PropertySerializer(serializers.ModelSerializer):
    """This class handles serializing and deserializing of Property objects"""

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
