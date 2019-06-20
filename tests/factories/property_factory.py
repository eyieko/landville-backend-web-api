import factory
from faker import Faker

from django.utils.timezone import now

from property.models import (
    Property, PropertyEnquiry, PropertyInspection,
    PropertyReview, BuyerPropertyList)
from .authentication_factory import UserFactory, ClientFactory

fake = Faker()
address = {'City': fake.city(), 'Street': fake.street_name(),
           'State': fake.state()}
coordinates = {'lat': '25354.231', 'lon': '45235.0343'}


class PropertyFactory(factory.DjangoModelFactory):
    """This class creates fake property"""

    class Meta:
        model = Property

    title = fake.word()
    address = address
    coordinates = coordinates
    client = factory.SubFactory(ClientFactory)
    description = fake.sentences()
    list_date = now()
    price = 2452345234.43
    lot_size = 2345.435
    image_main = fake.url()
    image_others = [fake.url(), fake.url()]
    purchase_plan = 'I'


class PropertyEnquiryFactory(factory.DjangoModelFactory):
    """This class creates fake property enquiry"""

    class Meta:
        model = PropertyEnquiry

    target_property = factory.SubFactory(PropertyFactory)
    enquirer_name = fake.name()
    email = fake.email()
    phone = fake.phone_number()[:17]
    message = fake.sentences()


class PropertyReviewFactory(factory.DjangoModelFactory):
    """This class creates fake property reviews"""

    class Meta:
        model = PropertyReview

    reviewer = factory.SubFactory(UserFactory)
    target_property = factory.SubFactory(PropertyFactory)
    comment = fake.sentences()


class PropertyInspectionFactory(factory.DjangoModelFactory):
    """This calss creates fake property inspections"""

    class Meta:
        model = PropertyInspection

    requester = factory.SubFactory(UserFactory)
    target_property = factory.SubFactory(PropertyFactory)
    inspection_time = now()
    remarks = fake.sentences()


class BuyerPropertyListFactory(factory.DjangoModelFactory):
    """This calss creates fake property inspections"""

    class Meta:
        model = BuyerPropertyList

    buyer = factory.SubFactory(UserFactory)
    listed_property = factory.SubFactory(PropertyFactory)
