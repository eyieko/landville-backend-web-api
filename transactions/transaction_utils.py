import json
from transactions.models import Deposit, Savings, Transaction


def save_deposit(purpose,
                 references,
                 amount,
                 user,
                 property=None,
                 description="LandVille trans"):
    """
    after a successfull payment , we save the deposit in the table with
    the type as purpose
    Args:
        type (string): transaction type for now saving or buying
        references (dict): references from flutterwave
        amount (float): the transaction amount
        description (str, optional): [description].
        property_id (int, optional): if we are buying it's the
        property we are paying for otherwise it's null
        Defaults to "LandVille trans".
    Returns:
        (tuple): deposit, transaction the deposit and
        the saving or transaction according to the purpose
    """
    if purpose == 'Saving':
        defaults_val = {'balance': amount}
        saving, created = Savings.objects.get_or_create(owner=user,
                                                        defaults=defaults_val)
        if not created:
            saving.balance += amount
        deposit = Deposit(account=saving,
                          references=json.dumps(references),
                          amount=amount,
                          description=description)
        saving.save()
        deposit.save()
        return deposit, saving
    else:
        transaction, created = Transaction.objects.\
            get_or_create(target_property=property,
                          buyer=user,
                          defaults={'amount_payed': amount})
        if not created:
            transaction.amount_payed += amount
        deposit = Deposit(transaction=transaction,
                          references=json.dumps(references),
                          amount=amount,
                          description=description)
        transaction.save()
        deposit.save()
        return deposit, transaction
