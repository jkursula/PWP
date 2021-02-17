from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Transaction(db.Model):
    """
Current implementation:
- sender and receiver can be the same user
- category is mandatory
"""
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    dateTime = db.Column(db.DateTime, nullable=False) 
    senderId = db.Column(db.Integer, db.ForeignKey("user.id"))
    receiverId = db.Column(db.Integer, db.ForeignKey("user.id"))
    categoryId = db.Column(db.Integer, db.ForeignKey("category.id"))
    sender = db.relationship("User", back_populates="transaction")
    receiver = db.relationship("User", back_populates="transaction")
    category = db.relationship("Category", back_populates="transaction")

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categoryName = db.Column(db.String(64), nullable=False, unique=True)
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False, unique=True)
    bankAccountId = db.Column(db.Integer, db.ForeignKey("bankAccount.id"))
    bankAccount = db.relationship("BankAccount", back_populates="user")

class BankAccount(db.Model):
    __tablename__ = 'bankAccount'
    id = db.Column(db.Integer, primary_key=True)
    iban = db.Column(db.String(32), nullable=False, unique=True)
    bankName = db.Column(db.String(64), nullable=False, unique=False)
    user = db.relationship("User", back_populates="bankAccount")
    
