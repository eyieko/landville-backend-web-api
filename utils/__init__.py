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

