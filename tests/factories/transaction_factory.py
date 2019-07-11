import factory
import json
from faker import Faker
from ..factories.property_factory import PropertyFactory
from .authentication_factory import UserFactory, ClientFactory
from transactions.models import Transaction, Savings, Deposit, ClientAccount
from datetime import datetime

fake = Faker()


class JSONFactory(factory.DictFactory):
    """
    Use with factory.Dict to make JSON strings.
    """

    @classmethod
    def _generate(cls, create, attrs):
        obj = super()._generate(create, attrs)
        return json.dumps(obj)


class TransactionFactory(factory.DjangoModelFactory):
    """This class creates fake transactions"""

    class Meta:
        model = Transaction

    target_property = factory.SubFactory(PropertyFactory)
    amount_payed = 200000.00
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
    transaction = factory.SubFactory(TransactionFactory)
    references = factory.Dict(
        {
            'txRef': '{}_LAND{}'.format('TAX', datetime.now()),
            'orderRef': '{}_LAND{}'.format('ORDER', datetime.now()),
            'flwRef': '{}_LAND{}'.format('FLW', datetime.now()),
            'raveRef': '{}_LAND{}'.format('RAV', datetime.now()),
        },
        dict_factory=JSONFactory)
    amount = 2453534.54
    description = fake.text()


class ClientAccountFactory(factory.DjangoModelFactory):
    """This class creates fake client accounts"""

    class Meta:
        model = ClientAccount

    owner = factory.SubFactory(ClientFactory)
    bank_name = fake.company()
    account_number = str(fake.random.randint(1000000000, 100000000000))
    swift_code = str(fake.random.randint(1000000000, 100000000000))
