"""A module of serializer classes for the payment system"""

from rest_framework import serializers
from transactions.models import ClientAccount
from rest_framework.exceptions import ValidationError


class ClientAccountSerializer(serializers.ModelSerializer):
    """serializer class for the client account model"""

    def validate(self, data):
        acc_num = data['account_number']
        if len(acc_num) != 10 and not acc_num.isdigit():
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


class CardPaymentSerializer(serializers.Serializer):
    cardno = serializers.CharField(max_length=20)
    cvv = serializers.CharField(max_length=5)
    expirymonth = serializers.CharField(max_length=2)
    expiryyear = serializers.CharField(max_length=2)
    amount = serializers.FloatField(min_value=0.00)


class ForeignCardPaymentSerializer(CardPaymentSerializer):
    billingzip = serializers.CharField(max_length=10)
    billingcity = serializers.CharField(max_length=20)
    billingaddress = serializers.CharField(max_length=50)
    billingstate = serializers.CharField(max_length=20)
    billingcountry = serializers.CharField(max_length=20)


class PaymentValidationSerializer(serializers.Serializer):
    otp = serializers.IntegerField()
    flwRef = serializers.CharField(max_length=60)


class PinCardPaymentSerializer(CardPaymentSerializer):
    pin = serializers.IntegerField()
