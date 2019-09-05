import factory
from faker import Faker

from authentication.models import User, UserProfile, Client, \
    PasswordResetToken, ClientReview, ReplyReview, CardInfo


fake = Faker()
address = {'City': 'Nairobi', 'Street': 'Valley Road', 'State': 'Nairobi'}
role = "CA"


class UserFactory(factory.DjangoModelFactory):
    """This class will create test users"""

    class Meta:
        model = User

    username = factory.LazyAttribute(lambda _: fake.name())
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    # users are created with the default password of `password`
    password = factory.PostGenerationMethodCall('set_password',
                                                'password')
    email = factory.LazyAttribute(lambda _: fake.email())
    role = role


class ClientFactory(factory.DjangoModelFactory):
    """This class will create clients"""

    class Meta:
        model = Client

    client_name = factory.LazyAttribute(lambda _: fake.company())
    client_admin = factory.SubFactory(UserFactory)
    # phone number shouldn't be longer than 17 digits
    phone = factory.LazyAttribute(lambda _: fake.phone_number()[:17])
    address = address
    email = factory.sequence(lambda n: f'user_{n}@email.com')


class UserProfileFactory(factory.DjangoModelFactory):
    """This class will create user profiles"""

    class Meta:
        model = UserProfile

    user = factory.SubFactory(UserFactory)
    phone = factory.LazyAttribute(lambda _: fake.phone_number()[:17])
    address = address
    image = fake.url()
    security_question = fake.sentence()
    security_answer = fake.word()


class PasswordResetTokenFactory(factory.DjangoModelFactory):
    """ This class creates PasswordResetToken objects for testing."""

    class Meta:
        model = PasswordResetToken

    token = fake.text()
    is_valid = True


class ClientReviewsFactory(factory.DjangoModelFactory):
    """This class will create reviews on clients for testing """

    class Meta:
        model = ClientReview

    reviewer = factory.SubFactory(UserFactory)
    client = factory.SubFactory(ClientFactory)
    review = fake.sentences()


class ReplyReviewsFactory(factory.DjangoModelFactory):
    """This class will create replies to reviews"""

    class Meta:
        model = ReplyReview

    review = factory.SubFactory(ClientReviewsFactory)
    reviewer = factory.SubFactory(UserFactory)
    reply = fake.sentences()


class CardInfoFactory(factory.DjangoModelFactory):
    """This class will create cards"""

    class Meta:
        model = CardInfo

    embed_token = fake.text()
    card_number = fake.credit_card_number(card_type=None)
    card_expiry = fake.credit_card_expire(
        start="now", end="+10y", date_format="%m/%y"
        )
    card_brand = fake.word()
    user_id = factory.SubFactory(UserFactory)
