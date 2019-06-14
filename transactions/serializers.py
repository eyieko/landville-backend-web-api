from rest_framework import serializers
from transactions.models import ClientAccount
from rest_framework.exceptions import ValidationError


class ClientAccountSerializer(serializers.ModelSerializer):
    """serializer class for the client account model"""

    def validate(self, data):
        acc_num = data['account_number']
        if len(acc_num) != 10 and acc_num.isdigit() == False:
            raise ValidationError(
                'Your account number must be 10 digits and only intergers')

        if not data['swift_code'].isalpha():
            raise ValidationError(
                'Swift code must only be letters characters')

        return data

    class Meta:
        model = ClientAccount
        fields = ['bank_name', 'account_number', 'account_type', 'swift_code']

    def create(self, validated_data):
        bank_details = ClientAccount.objects.create(**validated_data)
        return bank_details

    def update(self, instance, validated_data):
        """update an existing account details and return them"""
        instance.bank_name = validated_data.get(
            'bank_name', instance.bank_name)
        instance.account_number = validated_data.get(
            'account_number', instance.account_number)
        instance.swift_code = validated_data.get(
            'swift_code', instance.swift_code)

        instance.save()
        return instance
