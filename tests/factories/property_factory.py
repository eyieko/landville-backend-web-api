import factory
from factory.faker import faker
from faker import Faker

from property.models import Property, PropertyEnquiry, PropertyInspection, PropertyReview
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
    property_type = fake.word()
    description = fake.sentences()
    list_date = fake.date_time()
    price = 2452345234.43
    lot_size = 2345.435
    image_main = fake.url()
    image_others = [fake.url(), fake.url()]
