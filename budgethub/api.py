from flask import Blueprint
from flask_restful import Api

from budgethub.resources.transaction import TransactionCollection, TransactionItem
from budgethub.resources.category import CategoryCollection, CategoryItem
from budgethub.resources.user import UserCollection, UserItem
from budgethub.resources.bank_account import BankAccountCollection, BankAccountItem

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

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