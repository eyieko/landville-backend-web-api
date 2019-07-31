from django.db import models
from django.contrib.postgres.fields import JSONField
from utils.models import BaseAbstractModel
from utils.managers import CustomQuerySet, ClientAccountQuery, TransactionQuery
from property.models import Property
from authentication.models import User, Client


class Transaction(BaseAbstractModel):
    """This class defines the Transaction model"""

    STATUS_CHOICES = (
        ('S', 'SUCCESSFUL'),
        ('P', 'PENDING'),
        ('F', 'FAILED'),
    )

    target_property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='transactions')
    buyer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='buyer')
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default='P')
    amount_paid = models.DecimalField(decimal_places=2,
                                      max_digits=14, default=0)
    objects = models.Manager()
    active_objects = TransactionQuery.as_manager()

    def __str__(self):
        return f'{self.status} transaction for {self.target_property}'


class Deposit(BaseAbstractModel):
    """This class defines the Deposit model for all Savings and transaction"""

    account = models.ForeignKey('Savings',
                                on_delete=models.CASCADE,
                                related_name='account',
                                default=None,
                                blank=True,
                                null=True)
    transaction = models.ForeignKey('Transaction',
                                    on_delete=models.CASCADE,
                                    related_name='deposits',
                                    default=None,
                                    blank=True,
                                    null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    references = JSONField(default=None, blank=False, null=False)
    description = models.TextField(max_length=500)
    objects = models.Manager()
    active_objects = CustomQuerySet.as_manager()

    def __str__(self):
        return f"{self.amount} amount deposit for {self.account}"


class Savings(BaseAbstractModel):
    """This class defines the Savings model"""

    owner = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='savings')
    balance = models.DecimalField(decimal_places=2, max_digits=14)

    objects = models.Manager()
    active_objects = CustomQuerySet.as_manager()

    def __str__(self):
        return f'Savings by {self.owner}'


class ClientAccount(BaseAbstractModel):
    """This class defines the Client Accounts model"""

    ACCOUNT_TYPES = (
        ('CRA', 'CREDIT ACCOUNT'),
        ('CUR', 'CURRENT ACCOUNT'),
        ('SAV', 'SAVINGS ACCOUNT'),
    )
    owner = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='account'
    )
    bank_name = models.CharField(max_length=150)
    account_number = models.CharField(max_length=50)
    account_type = models.CharField(
        max_length=3, choices=ACCOUNT_TYPES, default='CRA')
    swift_code = models.CharField(max_length=50)

    objects = models.Manager()
    active_objects = ClientAccountQuery.as_manager()

    def __str__(self):
        return f'{self.owner}\'s account for {self.bank_name}'
