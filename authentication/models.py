from django.db import models
from django.contrib.auth.models import (AbstractUser, BaseUserManager)
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime, timedelta
from django.conf import settings

from utils.models import BaseAbstractModel
from utils.managers import CustomQuerySet

import jwt


class UserManager(BaseUserManager):
    """
    We need to override the `create_user` method so that users can only be created
    when all non-nullable fields are populated.
    """

    def create_user(self, first_name=None, last_name=None, email=None, password=None):
        """Create and return a `User` with an email, username and password."""

        if not first_name:
            raise TypeError('Users must have a first name.')

        if not last_name:
            raise TypeError('Users must have a last name.')

        if not email:
            raise TypeError('Users must have an email address.')

        if not password:
            raise TypeError('Users must have a password.')

        user = self.model(first_name=first_name, last_name=last_name, email=self.normalize_email(
            email))
        user.set_password(password)
        user.is_active = False
        user.save()

        return user

    def create_superuser(self, first_name=None, last_name=None, email=None, password=None):
        """Create and return a `User` who is also a superuser"""
        if not first_name:
            raise TypeError('Superusers must have a first name.')

        if not last_name:
            raise TypeError('Superusers must have a last name.')

        if not email:
            raise TypeError('Superusers must have an email address.')

        if not password:
            raise TypeError('Superusers must have a password.')

        user = self.model(first_name=first_name, last_name=last_name, email=self.normalize_email(
            email), role='LA')
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.is_verified = True
        user.set_password(password)
        user.save()


class User(AbstractUser, BaseAbstractModel):
    """This class defines the User model"""

    USER_ROLES = (
        ('LA', 'LANDVILLE ADMIN'),
        ('CA', 'CLIENT ADMIN'),
        ('BY', 'BUYER'),
    )

    username = models.CharField(null=True, blank=True, max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(
        verbose_name='user role', max_length=2, choices=USER_ROLES, default='BY'
    )
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()
    active_objects = CustomQuerySet.as_manager()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def token(self):
        exp = datetime.now() - timedelta(days=1)
        token = jwt.encode({
            'id': self.pk,
            'exp': int(exp.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')
        return token.decode('utf-8')


class UserProfile(BaseAbstractModel):
    """This class defines a Profile model for all Users"""

    LEVEL_CHOICES = (
        ('S', 'STARTER'),
        ('B', 'BUYER'),
        ('I', 'INVESTOR')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=17, unique=True)
    address = JSONField(
        verbose_name='physical address', encoder=DjangoJSONEncoder
    )
    user_level = models.CharField(
        verbose_name='user level', max_length=1, default='S',
        choices=LEVEL_CHOICES
    )
    image = models.URLField(null=True, blank=True)
    security_question = models.TextField(null=True, blank=True)
    security_answer = models.CharField(max_length=100, null=True, blank=True)

    objects = models.Manager()
    active_objects = CustomQuerySet.as_manager()

    def __str__(self):
        return f"{self.user}'s Profile"


class Client(BaseAbstractModel):
    """This class defines the model for Clients"""

    client_name = models.CharField(max_length=100, unique=True)
    client_admin = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='employer'
    )
    phone = models.CharField(max_length=17, unique=True)
    email = models.EmailField()
    address = JSONField(
        verbose_name='physical address', encoder=DjangoJSONEncoder
    )

    objects = models.Manager()
    active_objects = CustomQuerySet.as_manager()

    def __str__(self):
        return self.client_name
