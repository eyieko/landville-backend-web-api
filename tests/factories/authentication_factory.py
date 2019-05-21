import factory
from factory.faker import faker
from faker import Faker

from authentication.models import User, UserProfile, Client

fake = Faker()
address = {'City': 'Nairobi', 'Street': 'Valley Road', 'State': 'Nairobi'}


class UserFactory(factory.DjangoModelFactory):
    """This class will create test users"""

    class Meta:
        model = User

    username = fake.user_name()
    first_name = fake.first_name()
    last_name = fake.last_name()
    password = fake.password()
    is_verified = True  # verify users so they can easily log in when testing
    email = fake.email()


class ClientFactory(factory.DjangoModelFactory):
    """This class will create clients"""

    class Meta:
        model = Client

    client_name = fake.company()
    client_admin = factory.SubFactory(UserFactory)
    # phone number shouldn't be longer than 17 digits
    phone = fake.phone_number()[:17]
    address = address
    email = fake.email()


class UserProfileFactory(factory.DjangoModelFactory):
    """This class will create user profiles"""

    class Meta:
        model = UserProfile

    user = factory.SubFactory(UserFactory)
    phone = fake.phone_number()[:17]
    address = address
    image = fake.url()
    security_question = fake.sentence()
    security_answer = fake.word()
