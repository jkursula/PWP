from datetime import datetime
from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

import click
from flask.cli import with_appcontext

from budgethub import db


##Association tables
transaction_category_association_table = db.Table('transaction_category_association_table',
    db.Column('transactionId', db.Integer, db.ForeignKey('transaction.id'), primary_key=True),
    db.Column('categoryId', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

bankaccount_user_association_table = db.Table('bankaccount_user_association_table',
    db.Column('bankAccountId', db.Integer, db.ForeignKey('bankAccount.id'), primary_key=True),
    db.Column('userId', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)


##DB models
class Transaction(db.Model):
    """
Current implementation:
- sender and receiver can be the same user
"""
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    dateTime = db.Column(db.DateTime, nullable=False) 
    senderId = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"))
    receiverId = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"))
    sender = db.relationship("User", foreign_keys=[senderId])
    receiver = db.relationship("User", foreign_keys=[receiverId])
    category = db.relationship("Category", secondary=transaction_category_association_table, back_populates="transaction")

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    categoryName = db.Column(db.String(64), nullable=False, unique=True)
    transaction = db.relationship("Transaction", secondary=transaction_category_association_table, back_populates="category")
    
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False, unique=False)
    bankAccount = db.relationship("BankAccount",secondary=bankaccount_user_association_table, back_populates="user")

class BankAccount(db.Model):
    __tablename__ = 'bankAccount'
    id = db.Column(db.Integer, primary_key=True)
    iban = db.Column(db.String(32), nullable=False, unique=True)
    bankName = db.Column(db.String(64), nullable=False, unique=False)
    user = db.relationship("User",secondary=bankaccount_user_association_table, back_populates="bankAccount")


## command line commands
@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()