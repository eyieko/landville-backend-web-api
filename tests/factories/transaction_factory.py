import factory
from factory.faker import faker
from faker import Faker

from ..factories.property_factory import PropertyFactory
from .authentication_factory import UserFactory, ClientFactory
from transactions.models import Transaction, Savings, Deposit, ClientAccount

fake = Faker()


class TransactionFactory(factory.DjangoModelFactory):
    """This class creates fake transactions"""

    class Meta:
        model = Transaction

    target_property = factory.SubFactory(PropertyFactory)
    buyer = factory.SubFactory(UserFactory)


class SavingsFactory(factory.DjangoModelFactory):
    """This class creates fake savings"""

    class Meta:
        model = Savings

    owner = factory.SubFactory(UserFactory)
    balance = 24523453.45


class DepositFactory(factory.DjangoModelFactory):
    """This class creates fake deposits"""

    class Meta:
        model = Deposit

    account = factory.SubFactory(SavingsFactory)
    amount = 2453534.54
    description = fake.sentences()


class ClientAccountFactory(factory.DjangoModelFactory):
    """This class creates fake client accounts"""

    class Meta:
        model = ClientAccount

    owner = factory.SubFactory(ClientFactory)
    bank_name = fake.company()
    account_number = str(fake.random.randint(1000000000, 100000000000))
    account_type = fake.word()
    swift_code = str(fake.random.randint(1000000000, 100000000000))
