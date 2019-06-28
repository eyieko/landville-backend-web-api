from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.core.serializers.json import DjangoJSONEncoder

from utils.models import BaseAbstractModel
from utils.managers import CustomQuerySet, PropertyQuery, PropertyEnquiryQuery
from authentication.models import User, Client
from utils.slug_generator import generate_unique_slug
import uuid


# assiging this as a global variable makes it easier to access it
# and use it for validators in other areas. There is now only one place
# to change if you want to alter this attribute.
MAX_PROPERTY_IMAGE_COUNT = 15


class Property(BaseAbstractModel):
    """This class defines the Property model"""

    PURCHASE_CHOICES = (
        ('I', 'INSTALLMENTS'),
        ('F', 'FULL PAYMENT')
    )

    PROPERTY_TYPES = (
        ('B', 'BUILDING'),
        ('E', 'EMPTY LOT'),
    )

    title = models.CharField(max_length=255)
    address = JSONField(encoder=DjangoJSONEncoder)
    coordinates = JSONField(encoder=DjangoJSONEncoder)
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='properties')
    property_type = models.CharField(
        max_length=1, choices=PROPERTY_TYPES, default='B')
    description = models.TextField()
    list_date = models.DateField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    is_sold = models.BooleanField(default=False)
    sold_at = models.DateTimeField(null=True, blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=14)
    bedrooms = models.IntegerField(null=True, blank=True)
    bathrooms = models.IntegerField(null=True, blank=True)
    garages = models.IntegerField(null=True, blank=True)
    lot_size = models.DecimalField(decimal_places=4, max_digits=8)
    image_main = models.URLField()
    image_others = ArrayField(models.URLField(
        unique=True), size=MAX_PROPERTY_IMAGE_COUNT, blank=True, default=list)
    video = models.URLField(unique=True, blank=True, null=True)
    view_count = models.IntegerField(default=0)
    last_viewed = models.DateTimeField(null=True, blank=True)
    purchase_plan = models.CharField(max_length=1, choices=PURCHASE_CHOICES)
    slug = models.SlugField(max_length=250, unique=True)

    objects = models.Manager()
    active_objects = PropertyQuery.as_manager()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Saves all the changes of the Property model"""
        if not self.slug:
            self.slug = generate_unique_slug(
                self, 'slug')
        super().save(*args, **kwargs)


class PropertyEnquiry(BaseAbstractModel):
    """This class defines the model for enquiries that are made by the user"""

    enquiry_id = models.CharField(
        max_length=100, blank=True, unique=True, default=uuid.uuid4)
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='client')
    requester = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='enquiry_requester')
    target_property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='enquired_property')
    visit_date = models.DateTimeField()
    message = models.TextField(max_length=1000)
    is_resolved = models.BooleanField(default=False)

    objects = models.Manager()
    active_objects = PropertyEnquiryQuery.as_manager()

    def __str__(self):
        return f'Enquiry {self.enquiry_id} by {self.requester}'


class PropertyInspection(BaseAbstractModel):
    """This class defines the model for property inspections"""

    INSPECTION_CHOICES = (
        ('P', 'PHYSICAL INSPECTION'),
        ('V', 'VIDEO INSPECTION'),
    )

    requester = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='requesters')
    target_property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='inspected_property')
    inspection_time = models.DateTimeField()
    remarks = models.TextField()
    inspection_mode = models.CharField(
        max_length=1, choices=INSPECTION_CHOICES, default='P')

    objects = models.Manager()
    active_objects = CustomQuerySet.as_manager()

    def __str__(self):
        return f'Inspection by {self.requester} due on {self.inspection_time}'


class PropertyReview(BaseAbstractModel):
    """This class defines the model for the property reviews"""

    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviewers')
    target_property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='reviewed_property')
    comment = models.TextField()
    is_published = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = CustomQuerySet.as_manager()

    def __str__(self):
        return f'Review by {self.reviewer} on {self.created_at}'


class BuyerPropertyList(BaseAbstractModel):
    """
    Model for buyers' property list. Contains
    list of properties a buyer may be interested
    in.
    """

    buyer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='property_of_interest')
    listed_property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='property')

    objects = models.Manager()
    active_objects = CustomQuerySet.as_manager()

    def __str__(self):
        return 'Buyer list for: ' + str(self.buyer.email)
