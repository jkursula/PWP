from flask import Blueprint
from flask_restful import Api

from budgethub.resources.transaction import TransactionCollection, TransactionItem
from budgethub.resources.category import CategoryCollection, CategoryItem
from budgethub.resources.user import UserCollection, UserItem
from budgethub.resources.bank_account import BankAccountCollection, BankAccountItem

api_bp = Blueprint("api", __name__, url_prefix="/api/")
api = Api(api_bp)

##Routing
#transactions routing
api.add_resource(TransactionCollection, "/transactions/")
api.add_resource(TransactionItem, "/transactions/<transaction_id>/")

#categories routing
api.add_resource(CategoryCollection, "/categories/")
api.add_resource(CategoryItem, "/categories/<category_name>/")

#users routing
api.add_resource(UserCollection, "/users/")
api.add_resource(UserItem, "/users/<username>/")

#bank account routing
api.add_resource(BankAccountCollection, "/bankaccounts/")
api.add_resource(BankAccountItem, "/bankaccounts/<iban>/")