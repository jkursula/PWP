import os
import random
import pytest
import tempfile

from datetime import datetime
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

from budgethub import db, create_app
from budgethub.models import Transaction, BankAccount, User, Category
import tests.utils as utils

app = create_app()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture
def client():
    db_fd, db_fname = tempfile.mkstemp()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        yield app.test_client()
        
    db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)



def test_create_instances(client):
    """
    Tests that we can create one instance of each model and save them to the
    database using valid values for all columns. After creation, test that
    everything can be found from database, and that all relationships have been
    saved correctly.
    """

    # Create everything
    bankAccount1 = utils._get_bankAccount(iban="FI01", bankName="The bank")
    bankAccount2 = utils._get_bankAccount(iban="FI02", bankName="The bank")
    user1 = utils._get_user(username="user1", password="password")
    user2 = utils._get_user(username="user2", password="password2")
    user1.bankAccount.append(bankAccount1)
    user2.bankAccount.append(bankAccount2)
    category1 = utils._get_category(name="cat1")
    category2 = utils._get_category(name="cat2")
    transaction = utils._get_transaction(price=3.50, dateTime=datetime.now(), sender=user1, receiver=user2,
                                   category=[category1])

    db.session.add(bankAccount1)
    db.session.add(bankAccount2)
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(category1)
    db.session.add(category2)
    db.session.add(transaction)
    db.session.commit()

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

def test_update_instances(client):
    """
    First instances are created and then updated. Lastly the instances are checked to have the updated attributes.
    """
    #create instances
    bankAccount1 = utils._get_bankAccount(iban="FI03", bankName="The bank")
    bankAccount2 = utils._get_bankAccount(iban="FI04", bankName="The bank")
    user1 = utils._get_user(username="user3", password="passwor3")
    user2 = utils._get_user(username="user4", password="password4")
    user1.bankAccount.append(bankAccount1)
    user2.bankAccount.append(bankAccount2)
    category1 = utils._get_category(name="cat3")
    category2 = utils._get_category(name="cat4")
    transaction = utils._get_transaction(price=9.99, dateTime=datetime.now(), sender=user1, receiver=user2,
                                   category=[category1])

    db.session.add(bankAccount1)
    db.session.add(bankAccount2)
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(category1)
    db.session.add(category2)
    db.session.add(transaction)
    db.session.commit()
    #update instances
    user1.bankAccount.append(bankAccount2)
    user2.bankAccount.append(bankAccount1)
    transaction.sender = User.query.filter_by(username="user4").first()
    category1.categoryName = "dog"
    bankAccount1.bankName = "The other bank"
    db.session.commit()
    #check that instances are updated correctly
    db_user1 = User.query.filter_by(username="user3").first()
    db_user2 = User.query.filter_by(username="user4").first()
    db_transaction = Transaction.query.filter_by(id=1).first()
    
    assert db_user1.bankAccount == [bankAccount1, bankAccount2]
    assert db_user2.bankAccount == [bankAccount2, bankAccount1]
    assert db_transaction.sender == User.query.filter_by(username="user4").first()
    assert Category.query.filter_by(categoryName="dog").first().categoryName == "dog"
    assert BankAccount.query.filter_by(bankName="The other bank").first().bankName == "The other bank"


def test_delete_instances(client):
    """
    Tests that instances behave correctly when deleted.
    """
    #create instances:
    #2 bankAccounts
    #2 Users
    #2 Categories
    #1 Transaction
    bankAccount1 = utils._get_bankAccount(iban="FI05", bankName="The bank")
    bankAccount2 = utils._get_bankAccount(iban="FI06", bankName="The bank")
    user1 = utils._get_user(username="user3", password="passwor3")
    user2 = utils._get_user(username="user4", password="password4")
    user1.bankAccount.append(bankAccount1)
    user2.bankAccount.append(bankAccount2)
    category1 = utils._get_category(name="cat3")
    category2 = utils._get_category(name="cat4")
    transaction = utils._get_transaction(price=9.99, dateTime=datetime.now(), sender=user1, receiver=user2,
                                   category=[category1])

    db.session.add(bankAccount1)
    db.session.add(bankAccount2)
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(category1)
    db.session.add(category2)
    db.session.add(transaction)
    db.session.commit()
    #delete instances:
    #1 bankAccount
    #1 User
    #1 Category
    #1 Transaction
    db.session.delete(user1)
    db.session.delete(bankAccount2)
    db.session.delete(category2)
    db.session.delete(transaction)
    db.session.commit()
    #after deleting should be only one instance of
    #user, bankaccount, and category and no instances of transaction
    assert BankAccount.query.count() == 1
    assert User.query.count() == 1
    assert Category.query.count() == 1
    assert Transaction.query.count() == 0

def test_errors(client):
    """
    Test that the correct errors are raised in situations where they should be raised.
    """
    #two bankaccounts with the same iban should raise IntegrityError
    bankAccount1 = utils._get_bankAccount(iban="FI01", bankName="The bank")
    bankAccount2 = utils._get_bankAccount(iban="FI01", bankName="The bank")
    db.session.add(bankAccount1)
    db.session.add(bankAccount2)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()

    #two users with the same username should raise IntegrityError
    user1 = utils._get_user(username="user1", password="passwor3")
    user2 = utils._get_user(username="user1", password="password4")
    db.session.add(user1)
    db.session.add(user2)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()

    #two categories with the same name should raise IntegrityError
    category1 = utils._get_category(name="cat1")
    category2 = utils._get_category(name="cat1")
    db.session.add(category1)
    db.session.add(category2)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


    #creating two new users for transaction
    user3 = utils._get_user(username="user3", password="password4")
    user4 = utils._get_user(username="user4", password="password4")
    db.session.add(user3)
    db.session.add(user4)
    db.session.commit()

    #transaction with price other than float should raise StatementError
    transaction = utils._get_transaction(price="en kerro", dateTime=datetime.now(), sender=user3, receiver=user4,
                                   category=[category1])
    db.session.add(transaction)
    with pytest.raises(StatementError):
        db.session.commit()
    db.session.rollback()

    #transaction with dateTime other than datetime should raise StatementError
    transaction = utils._get_transaction(price=9.99, dateTime="en kerro", sender=user3, receiver=user4,
                                   category=[category1])
    db.session.add(transaction)
    with pytest.raises(StatementError):
        db.session.commit()
    db.session.rollback()