import json

from flask_restful import Resource, Api
#models
from datetime import datetime
from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

#resources
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import IntegrityError


##URL constants
MASON = "application/vnd.mason+json"
ERROR_PROFILE = "/profiles/error/"
LINK_RELATIONS_URL = "/storage/link-relations/"
TRANSACTION_PROFILE = "/profiles/transaction/"
CATEGORY_PROFILE = "/profiles/category/"
USER_PROFILE = "/profiles/user/"
BANK_ACCOUNT_PROFILE = "/profiles/bank-account/"

##app and api setup
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
api = Api(app)

##Dummy views
@app.route("/bumeta/link-relations/")
def link_relations():
    return("Hello :)")

@app.route("/profiles/product/")
def profiles_product():
    return("Hello :)")

@app.route("/profiles/error/")
def profiles_error():
    return("Hello :)")


##API resources
#Transaction resources
class TransactionCollection(Resource):
    def get(self):
        pass

    def post(self):
        pass

class TransactionItem(Resource):
    def get(self):
        pass

    def delete(self):
        pass

#Category resources
class CategoryCollection(Resource):
    def get(self):
        pass

    def post(self):
        pass

class CategoryItem(Resource):
    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

#User resources
class UserCollection(Resource):
    def get(self):
        pass

    def post(self):
        pass

class UserItem(Resource):
    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

#Bank account resources
class BankAccountCollection(Resource):
    def get(self):
        pass

    def post(self):
        pass

class BankAccountItem(Resource):
    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass


##Masonbuilder
class MasonBuilder(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.

        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.

        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.

        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, href, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.

        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md

        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href


## Extended Mason classes
#Transaction builder
class TransactionBuilder(MasonBuilder):
    @staticmethod
    def transaction_schema():
        pass

    def add_control_all_transactions(self):
        pass

    def add_control_add_transaction(self):
        pass
    
    def add_control_delete_transaction(self, transaction_id):
        pass

#category builder
class CategoryBuilder(MasonBuilder):
    @staticmethod
    def category_schema():
        pass

    def add_control_all_categories(self):
        pass

    def add_control_add_category(self):
        pass
    
    def add_control_delete_category(self, category_name):
        pass

    def add_control_edit_category(self, category_name):
        pass

#user builder
class UserBuilder(MasonBuilder):
    @staticmethod
    def user_schema():
        pass

    def add_control_all_users(self):
        pass

    def add_control_add_user(self):
        pass
    
    def add_control_delete_user(self, username):
        pass

    def add_control_edit_user(self, username):
        pass

#bank account builder
class BankAccountBuilder(MasonBuilder):
    @staticmethod
    def bank_account_schema():
        pass

    def add_control_all_bank_accounts(self):
        pass

    def add_control_add_bank_account(self):
        pass
    
    def add_control_delete_bank_account(self, bank_account_id):
        pass

    def add_control_edit_bank_account(self, bank_account_id):
        pass

##Create MASON error messages
def create_error_response(status_code, title, message=None):
    resource_url = request.path
    body = MasonBuilder(resource_url=resource_url)
    body.add_error(title, message)
    body.add_control("profile", href=ERROR_PROFILE)
    return Response(json.dumps(body), status_code, mimetype=MASON)

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
    

##Routing
#transactions routing
api.add_resource(TransactionCollection, "/api/transactions/")
api.add_resource(TransactionItem, "/api/transactions/<transaction>/")

#categories routing
api.add_resource(CategoryCollection, "/api/categories/")
api.add_resource(CategoryItem, "/api/categories/<categoryname>/")

#users routing
api.add_resource(UserCollection, "/api/users/")
api.add_resource(UserItem, "/api/users/<username>")

#bank account routing
api.add_resource(BankAccountCollection, "/api/bankaccounts/")
api.add_resource(BankAccountItem, "/api/bankaccounts/<bankaccount>/")
