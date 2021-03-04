import os
import random
import pytest
import tempfile

# import app
from datetime import datetime

from app import app, db, Transaction, Category, User, BankAccount
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import StatementError
from sqlalchemy import event




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

def test_update_instances(db_handle):
    """
    First instances are created and then updated. Lastly the instances are checked to have the updated attributes.
    """
    #create instances
    bankAccount1 = _get_bankAccount(iban="FI03", bankName="The bank")
    bankAccount2 = _get_bankAccount(iban="FI04", bankName="The bank")
    user1 = _get_user(username="user3", password="passwor3")
    user2 = _get_user(username="user4", password="password4")
    user1.bankAccount.append(bankAccount1)
    user2.bankAccount.append(bankAccount2)
    category1 = _get_category(name="cat3")
    category2 = _get_category(name="cat4")
    transaction = _get_transaction(price=9.99, dateTime=datetime.now(), sender=user1, receiver=user2,
                                   category=[category1])

    db_handle.session.add(bankAccount1)
    db_handle.session.add(bankAccount2)
    db_handle.session.add(user1)
    db_handle.session.add(user2)
    db_handle.session.add(category1)
    db_handle.session.add(category2)
    db_handle.session.add(transaction)
    db_handle.session.commit()
    #update instances
    user1.bankAccount.append(bankAccount2)
    user2.bankAccount.append(bankAccount1)
    transaction.sender = User.query.filter_by(username="user4").first()
    category1.categoryName = "dog"
    bankAccount1.bankName = "The other bank"
    db_handle.session.commit()
    #check that instances are updated correctly
    db_user1 = User.query.filter_by(username="user3").first()
    db_user2 = User.query.filter_by(username="user4").first()
    db_transaction = Transaction.query.filter_by(id=1).first()
    
    assert db_user1.bankAccount == [bankAccount1, bankAccount2]
    assert db_user2.bankAccount == [bankAccount2, bankAccount1]
    assert db_transaction.sender == User.query.filter_by(username="user4").first()
    assert Category.query.filter_by(categoryName="dog").first().categoryName == "dog"
    assert BankAccount.query.filter_by(bankName="The other bank").first().bankName == "The other bank"


def test_delete_instances(db_handle):
    """
    Tests that instances behave correctly when deleted.
    """
    #create instances:
    #2 bankAccounts
    #2 Users
    #2 Categories
    #1 Transaction
    bankAccount1 = _get_bankAccount(iban="FI05", bankName="The bank")
    bankAccount2 = _get_bankAccount(iban="FI06", bankName="The bank")
    user1 = _get_user(username="user3", password="passwor3")
    user2 = _get_user(username="user4", password="password4")
    user1.bankAccount.append(bankAccount1)
    user2.bankAccount.append(bankAccount2)
    category1 = _get_category(name="cat3")
    category2 = _get_category(name="cat4")
    transaction = _get_transaction(price=9.99, dateTime=datetime.now(), sender=user1, receiver=user2,
                                   category=[category1])

    db_handle.session.add(bankAccount1)
    db_handle.session.add(bankAccount2)
    db_handle.session.add(user1)
    db_handle.session.add(user2)
    db_handle.session.add(category1)
    db_handle.session.add(category2)
    db_handle.session.add(transaction)
    db_handle.session.commit()
    #delete instances:
    #1 bankAccount
    #1 User
    #1 Category
    #1 Transaction
    db_handle.session.delete(user1)
    db_handle.session.delete(bankAccount2)
    db_handle.session.delete(category2)
    db_handle.session.delete(transaction)
    db_handle.session.commit()
    #after deleting should be only one instance of
    #user, bankaccount, and category and no instances of transaction
    assert BankAccount.query.count() == 1
    assert User.query.count() == 1
    assert Category.query.count() == 1
    assert Transaction.query.count() == 0

def test_errors(db_handle):
    """
    Test that the correct errors are raised in situations where they should be raised.
    """
    #two bankaccounts with the same iban should raise IntegrityError
    bankAccount1 = _get_bankAccount(iban="FI01", bankName="The bank")
    bankAccount2 = _get_bankAccount(iban="FI01", bankName="The bank")
    db_handle.session.add(bankAccount1)
    db_handle.session.add(bankAccount2)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
    db_handle.session.rollback()

    #two users with the same username should raise IntegrityError
    user1 = _get_user(username="user1", password="passwor3")
    user2 = _get_user(username="user1", password="password4")
    db_handle.session.add(user1)
    db_handle.session.add(user2)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
    db_handle.session.rollback()

    #two categories with the same name should raise IntegrityError
    category1 = _get_category(name="cat1")
    category2 = _get_category(name="cat1")
    db_handle.session.add(category1)
    db_handle.session.add(category2)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
    db_handle.session.rollback()


    #creating two new users for transaction
    user3 = _get_user(username="user3", password="password4")
    user4 = _get_user(username="user4", password="password4")
    db_handle.session.add(user3)
    db_handle.session.add(user4)
    db_handle.session.commit()

    #transaction with price other than float should raise StatementError
    transaction = _get_transaction(price="en kerro", dateTime=datetime.now(), sender=user3, receiver=user4,
                                   category=[category1])
    db_handle.session.add(transaction)
    with pytest.raises(StatementError):
        db_handle.session.commit()
    db_handle.session.rollback()

    #transaction with dateTime other than datetime should raise StatementError
    transaction = _get_transaction(price=9.99, dateTime="en kerro", sender=user3, receiver=user4,
                                   category=[category1])
    db_handle.session.add(transaction)
    with pytest.raises(StatementError):
        db_handle.session.commit()
    db_handle.session.rollback()