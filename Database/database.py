from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    dateTime = db.Column(db.DateTime, nullable=False) 
    sender = db.Column(db.Integer, nullable=False) #tarvitsee relaation
    receiver = db.Column(db.Integer, nullable=False) #tarvitsee relaation
    category = db.Column(db.Integer, nullable=False) #Tarvitsee relaation 

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categoryName = db.Column(db.String(64), nullable=False, unique=True)
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(64), nullable=False, unique=True)
    passWord = db.Column(db.String(64), nullable=False, unique=True)

class BankAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(64), nullable=False, unique=True)
    bankName = db.Column(db.String(64), nullable=False, unique=False)
    
