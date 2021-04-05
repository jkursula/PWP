from datetime import datetime

from budgethub import db, create_app
from budgethub.models import *

#development app
app = create_app()

def _get_bankAccount(iban, bankName):
    return BankAccount(
        iban=iban,
        bankName=bankName
    )


def _get_user(username, password):
    return User(
        username=username,
        password=password
    )


def _get_category(name):
    return Category(
        categoryName=name
    )


def _get_transaction(price, dateTime, sender, receiver, category):
    return Transaction(
        price=price,
        dateTime=dateTime,
        sender=sender,
        receiver=receiver,
        category=category
    )

def populate_db():

    bankAccount1 = _get_bankAccount(iban="FI01", bankName="The bank")
    bankAccount2 = _get_bankAccount(iban="FI02", bankName="The bank")
    user1 = _get_user(username="user1", password="password")
    user2 = _get_user(username="user2", password="password2")
    user1.bankAccount.append(bankAccount1)
    user2.bankAccount.append(bankAccount2)
    category1 = _get_category(name="cat1")
    category2 = _get_category(name="cat2")
    transaction = _get_transaction(price=3.50, dateTime=datetime.now(), sender=user1, receiver=user2,
                                    category=[category1])

    db.session.add(bankAccount1)
    db.session.add(bankAccount2)
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(category1)
    db.session.add(category2)
    db.session.add(transaction)
    db.session.commit()

    
with app.app_context():
    populate_db()