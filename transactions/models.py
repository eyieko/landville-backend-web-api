from django.db import models

from utils.models import BaseAbstractModel
from utils.managers import CustomQuerySet
from property.models import Property
from authentication.models import User


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

    objects = models.Manager()
    active_objects = CustomQuerySet.as_manager()

    def __str__(self):
        return f"{self.status} transaction for {self.target_property}"


class Deposit(BaseAbstractModel):
    """This class defines the Deposit model for all Savings"""

    account = models.ForeignKey(
        'Savings', on_delete=models.CASCADE, related_name='account')
    amount = models.DecimalField(decimal_places=3, max_digits=12)
    description = models.TextField(max_length=500)

    objects = models.Manager()
    active_objects = CustomQuerySet.as_manager()

    def __str__(self):
        return f"{self.amount} amount deposit for {self.account}"


class Savings(BaseAbstractModel):
    """This class defines the Savings model"""

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='savings')
    balance = models.DecimalField(decimal_places=3, max_digits=14)

    objects = models.Manager()
    active_objects = CustomQuerySet.as_manager()

    def __str__(self):
        return f"Savings by {self.owner}"
