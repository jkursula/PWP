import json
from flask import request, Response, url_for

from budgethub.constants import *
from budgethub.models import *

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
        schema = {
            "type": "object",
            "required": ["price", "datetime", "sender", "receiver"]
        }
        props = schema["properties"] = {}
        props["id"] = {
            "description": "Transaction's unique id",
            "type": "number"
        }
        props["price"] = {
            "description": "Transaction's amount",
            "type": "number"
        }
        props["datetime"] = {
            "description": "Transaction's timestamp",
            "type": "string"
            #TODO:enable pattern
            # "pattern": "^[0-9]{4}-[01][0-9]-[0-3][0-9]$" 2021-04-03
        }
        props["sender"] = {
            "description": "Transaction's sender",
            "type": "string"
        }
        props["receiver"] = {
            "description": "Transaction's receiver",
            "type": "string"
        }
        props["category"] = {
            "description": "Transaction's category",
            #TODO: onko string vai lista?
            "type": "array"
        }
        return schema


    def add_control_all_transactions(self):
        self.add_control(
            "bumeta:transactions-all",
            "/api/transactions/",
            method="GET",
            title="Leads to the list of all transactions"
        )

    def add_control_add_transaction(self):
        self.add_control(
            ctrl_name="bumeta:add-transaction",
            href="api/transactions/",
            method="POST",
            encoding="json",
            schema=self.transaction_schema()
        )
    
    def add_control_delete_transaction(self, transaction_id):
        self.add_control(
            ctrl_name="bumeta:delete",
            href=url_for("api.transactionitem", transaction_id=transaction_id),
            method="DELETE",
            title="Delete this resource"
        )

#category builder
class CategoryBuilder(MasonBuilder):
    @staticmethod
    def category_schema():
        schema = {
            "type": "object",
            "required": ["category_name"]
        }
        props = schema["properties"] = {}
        props["category_name"] = {
            "description": "Categorie's unique name",
            "type": "string"
        }

        return schema

    def add_control_all_categories(self):
        self.add_control(
            "bumeta:categories-all",
            "/api/categories/",
            method="GET",
            title="Leads to the list of all categories"
        )

    def add_control_add_category(self):
        self.add_control(
            ctrl_name="bumeta:add-category",
            href="api/categories/",
            method="POST",
            encoding="json",
            schema=self.category_schema()
        )
    
    def add_control_delete_category(self, category_name):
        self.add_control(
            ctrl_name="bumeta:delete",
            href=url_for("api.categoryitem", category_name=category_name),
            method="DELETE",
            title="Delete this resource"
        )

    def add_control_edit_category(self, category_name):
        self.add_control(
            ctrl_name="edit",
            href=url_for("api.categoryitem", category_name=category_name),
            method="PUT",
            encoding="json",
            schema=self.category_schema()
        )

#user builder
class UserBuilder(MasonBuilder):
    @staticmethod
    def user_schema():
        schema = {
            "type": "object",
            "required": ["username"]
        }
        props = schema["properties"] = {}
        props["username"] = {
            "description": "User's unique username",
            "type": "string"
        }
        props["password"] = {
            "description": "User's password",
            "type": "string"
        }
        props["bankAccount"] = {
            "description": "User's bankAccount(s)",
            "type": "array"
        }

        return schema

    @staticmethod
    def create_user_schema():
        schema = {
            "type": "object",
            "required": ["username", "password"]
        }
        props = schema["properties"] = {}
        props["username"] = {
            "description": "User's unique username",
            "type": "string"
        }
        props["password"] = {
            "description": "User's password",
            "type": "string"
        }
        props["bankAccount"] = {
            "description": "User's bankAccount(s)",
            "type": "array"
        }

        return schema

    def add_control_all_users(self):
        self.add_control(
            "bumeta:users-all",
            "/api/users/",
            method="GET",
            title="Leads to the list of all users"
        )

    def add_control_add_user(self):
        self.add_control(
            ctrl_name="bumeta:add-user",
            href="api/users/",
            method="POST",
            encoding="json",
            schema=self.user_schema()
        )
    
    def add_control_delete_user(self, username):
        self.add_control(
            ctrl_name="bumeta:delete",
            href=url_for("api.useritem", username=username),
            method="DELETE",
            title="Delete this resource"
        )

    def add_control_edit_user(self, username):
        self.add_control(
            ctrl_name="edit",
            href=url_for("api.useritem", username=username),
            method="PUT",
            encoding="json",
            schema=self.user_schema()
        )

#bank account builder
class BankAccountBuilder(MasonBuilder):
    @staticmethod
    def bank_account_schema():
        schema = {
            "type": "object",
            "required": ["iban", "bankName"]
        }
        props = schema["properties"] = {}
        props["iban"] = {
            "description": "International bank account number",
            "type": "string"
        }
        props["bankName"] = {
            "description": "Bank's name",
            "type": "string"
        }

        return schema

    def add_control_all_bank_accounts(self):
        self.add_control(
            "bumeta:bank-accounts-all",
            "/api/bankaccounts/",
            method="GET",
            title="Leads to the list of all bank accounts"
        )

    def add_control_add_bank_account(self):
        self.add_control(
            ctrl_name="bumeta:add-bank-account",
            href="api/bankaccounts/",
            method="POST",
            encoding="json",
            schema=self.bank_account_schema()
        )
    
    def add_control_delete_bank_account(self, iban):
        self.add_control(
            ctrl_name="bumeta:delete",
            href=url_for("api.bankaccountitem", iban=iban),
            method="DELETE",
            title="Delete this resource"
        )

    def add_control_edit_bank_account(self, iban):
        self.add_control(
            ctrl_name="edit",
            href=url_for("api.bankaccountitem", iban=iban),
            method="PUT",
            encoding="json",
            schema=self.bank_account_schema()
        )

##Create MASON error messages
def create_error_response(status_code, title, message=None):
    resource_url = request.path
    body = MasonBuilder(resource_url=resource_url)
    body.add_error(title, message)
    body.add_control("profile", href=ERROR_PROFILE)
    return Response(json.dumps(body), status_code, mimetype=MASON)
