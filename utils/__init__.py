import re
from rest_framework import serializers


class BaseUtils():
    def remove_redundant_spaces(self, value):
        """
        Removes extra spaces from an input field
        """
        return re.sub(r'\s+', ' ', value).strip()

    def validate_data_instance(self, data, data_type, message):
        """Validate the data types of inputs"""
        if not isinstance(data, data_type):
            raise serializers.ValidationError(message)

    def validate_dictionary_keys(self, dict_key, dict_value, message):
        """Check for keys in the dictionary"""
        if dict_key not in [*dict_value]:
            raise serializers.ValidationError(message)

    def validate_empty_input(self, key_value, dict_value, message):
        """Check if input is empty"""
        if not dict_value[key_value].strip():
            raise serializers.ValidationError(message)

    def validate_phone_number(self, phone):
        """Validate the phone number to match expected format"""
        p = re.compile(r'\+?\d{3}\s?\d{3}\s?\d{7}')
        q = re.compile(r'^.{10,16}$')
        if not (p.match(phone) and q.match(phone)):
            raise serializers.ValidationError({
                "phone": "Phone number must be of the format +234 123 4567890"
            })

    def validate_dependent_fields(self, data, first_field, second_field,
                                  first_validation_error, second_validation_error):
        '''
        Function tests if the fields that depend on each other are both present
        in the user submitted data
        '''
        if first_field in data and not second_field in data:
            raise serializers.ValidationError({
                second_field: first_validation_error
            })

        if second_field in data and not first_field in data:
            raise serializers.ValidationError({
                first_field: second_validation_error
            })
