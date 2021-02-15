from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
"""
Current implementation:
- sender and receiver can be the same
- category is mandatory
"""
class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    dateTime = db.Column(db.DateTime, nullable=False) 
    sender = db.Column(db.Integer, db.ForeignKey("user.id"))
    receiver = db.Column(db.Integer, db.ForeignKey("user.id"))
    category = db.Column(db.Integer, db.ForeignKey("category.id"))

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categoryName = db.Column(db.String(64), nullable=False, unique=True)
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False, unique=True)
    bankAccountId = db.Column(db.Integer, db.ForeignKey("bankAccount.id"))

class BankAccount(db.Model):
    __tablename__ = 'bankAccount'
    id = db.Column(db.Integer, primary_key=True)
    iban = db.Column(db.String(32), nullable=False, unique=True)
    bankName = db.Column(db.String(64), nullable=False, unique=False)
    
