"""A module of serializer classes for the payment system"""

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from transactions.models import ClientAccount, Transaction
from property.models import Property
from property.serializers import PropertySerializer
from authentication.serializers import RegistrationSerializer
from authentication.models import User


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


class TransactionsSerializer(PropertySerializer):
    """Serializer for transactions"""
    percentage_completion = serializers.SerializerMethodField()
    deposits = serializers.SerializerMethodField()
    price = serializers.FloatField()
    buyer = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()
    total_amount_paid = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = ['title', 'buyer', 'price', 'total_amount_paid', 'balance', 'deposits',
                  'percentage_completion']

    def get_percentage_completion(self, obj):
        """Return the total percentage a user has so far paid for a property"""
        request = self.context.get('request')
        price = obj.price
        if request.user.role == 'BY':
            total_amount = Transaction.active_objects.total_amount(
                request.user, obj)
        else:
            total_amount = Transaction.active_objects.client_total_amount(obj)

        percentage = total_amount/price * 100
        # return a percentage as a 2 decimals value
        return "{:0.2f}".format(percentage)

    def get_deposits(self, obj):
        """Return all the deposits a user has made for a property"""
        transactions = Transaction.objects.filter(
            target_property__slug=obj.slug)
        deposits = []
        for transaction in transactions:
            data = {
                "date": transaction.created_at,
                "amount": transaction.amount
            }
            deposits.append(data)
        return deposits

    def get_buyer(self, obj):
        """Return the name of the user/buyer"""
        user = User.objects.get(pk=obj.transactions.first().buyer.pk)
        return user.email

    def get_total_amount_paid(self, obj):
        """Return the total amount paid by user for property so far"""
        request = self.context.get('request')
        if request.user.role == 'BY':
            total_amount = Transaction.active_objects.total_amount(
                request.user, obj)
        else:
            total_amount = Transaction.active_objects.client_total_amount(obj)
        return total_amount

    def get_balance(self, obj):
        """Return the balance the user is remaining with to complete payement"""
        request = self.context.get('request')
        price = obj.price
        if request.user.role == 'BY':
            total_amount = Transaction.active_objects.total_amount(
                request.user, obj)
        else:
            total_amount = Transaction.active_objects.client_total_amount(obj)

        balance = price - total_amount
        return balance


class CardPaymentSerializer(serializers.Serializer):
    cardno = serializers.CharField(max_length=20)
    cvv = serializers.CharField(max_length=5)
    expirymonth = serializers.CharField(max_length=2)
    expiryyear = serializers.CharField(max_length=2)
    amount = serializers.FloatField(min_value=0.00)
    save_card = serializers.BooleanField(default=False)


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


class CardlessPaymentSerializer(serializers.Serializer):
    amount = serializers.FloatField(min_value=0.00)
