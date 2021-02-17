import os
import pytest
import tempfile

import app
from datetime import datetime

from app import Transaction, Category, User, BankAccount
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy import event

##TODO: find out about using foreign keys


def _get_transaction(price=999999999.9, dateTime=datetime.now(), sender=1, receiver=1, category=1):
    return Transaction(
        price=price,
        dateTime=dateTime,
        sender=sender,
        receiver=receiver,
        category=category
    )

def _get_category():
    return Category(
        categoryName="cat"
    )
    
def _get_user(number=1):
    return User(
        username="user" + str(number),
        password="password"
    )
    
def _get_bankAccount(number=1):
    return BankAccount(
        iban="FI000000000000" + str(number),
        bankName="The bank"
    )

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

@pytest.fixture
def db_handle():
    db_fd, db_fname = tempfile.mkstemp()
    app.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.app.config["TESTING"] = True
    
    with app.app.app_context():
        app.db.create_all()
        
    yield app.db
    
    app.db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)


def test_create_bankAccount(db_handle):
    bankAccountRow = _get_bankAccount()
    db_handle.session.add(bankAccountRow)
    db_handle.session.commit()
    #If condition returns False, AssertionError is raised 
    assert BankAccount.query.count() == 1


def test_create_user(db_handle):
    bankAccountRow = _get_bankAccount()
    user = _get_user()
    db_handle.session.add(bankAccountRow)
    db_handle.session.add(user)
    db_handle.session.commit()
    #If condition returns False, AssertionError is raised 
    assert User.query.count() == 1

def test_create_category(db_handle):
    category = _get_category()
    db_handle.session.add(category)
    db_handle.session.commit()
    #If condition returns False, AssertionError is raised 
    assert Category.query.count() == 1

def test_create_transaction(db_handle):
    bankAccountRow1 = _get_bankAccount(1)
    bankAccountRow2 = _get_bankAccount(2)
    user1 = _get_user(1)
    user2 = _get_user(2)
    db_handle.session.add(bankAccountRow1)
    db_handle.session.add(bankAccountRow2)
    db_handle.session.add(user1)
    db_handle.session.add(user2)
    db_handle.session.commit()
    transaction = _get_transaction()
    db_handle.session.add(transaction)
    db_handle.session.commit()
    #If condition returns False, AssertionError is raised 
    assert Transaction.query.count() == 1


# def test_create_instances(db_handle):

    