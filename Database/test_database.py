import os
import random
import pytest
import tempfile

# import app
from datetime import datetime

from app import app, db, Transaction, Category, User, BankAccount
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy import event


##TODO: db_test.py does not work either...


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture
def db_handle():
    db_fd, db_fname = tempfile.mkstemp()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()

    yield db

    db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)


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


def test_create_instances(db_handle):
    """
    Tests that we can create one instance of each model and save them to the
    database using valid values for all columns. After creation, test that
    everything can be found from database, and that all relationships have been
    saved correctly.
    """

    # Create everything
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

    db_handle.session.add(bankAccount1)
    db_handle.session.add(bankAccount2)
    db_handle.session.add(user1)
    db_handle.session.add(user2)
    db_handle.session.add(category1)
    db_handle.session.add(category2)
    db_handle.session.add(transaction)
    db_handle.session.commit()

    # Check that everything exists
    assert BankAccount.query.count() == 2
    assert User.query.count() == 2
    assert Category.query.count() == 2
    assert Transaction.query.count() == 1
    db_bankAccounts = BankAccount.query.all()
    db_users = User.query.all()

    db_categories = Category.query.all()
    db_transaction = Transaction.query.first()

    # Check all relationships (both sides)

    assert db_transaction.sender in db_users
    assert db_transaction.receiver in db_users
    for category in db_transaction.category:
        assert category in db_categories
    for bankAccount in db_transaction.sender.bankAccount:
        assert bankAccount in db_bankAccounts

# def test_create_instances(db_handle):

