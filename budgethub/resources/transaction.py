from jsonschema import validate, ValidationError
from datetime import datetime

from flask_restful import Resource

from flask import Flask, Response, request, url_for
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import IntegrityError

from budgethub import db
from budgethub.models import *
from budgethub.constants import *
from budgethub.utils import *



#Transaction resources
class TransactionCollection(Resource):
    def get(self):
        body = TransactionBuilder()
        body.add_namespace("bumeta", LINK_RELATIONS_URL)
        body.add_control("self", "/api/users/")
        body.add_control_add_transaction()
        body.add_control_all_bank_accounts()
        body.add_control_all_categories()
        body.add_control_all_users()

        items = []
        for transaction in Transaction.query.all():
            transaction_item_body = TransactionBuilder(
                id = transaction.id,
                price = transaction.price,
                dateTime = str(transaction.dateTime),
                sender = transaction.sender.username,
                receiver = transaction.receiver.username,
                category = [cat.categoryName for cat in transaction.category]
            )
            transaction_item_body.add_control("self", url_for("api.transactionitem", transaction_id=transaction.id))
            transaction_item_body.add_control("profile", TRANSACTION_PROFILE)
            items.append(transaction_item_body)
        body["items"] = items

        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self):
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, TransactionBuilder.transaction_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        db_sender = User.query.filter_by(username=request.json["sender"]).first()
        if db_sender is None:
            return create_error_response(
                404, "Not found",
                "No user was found with the username {}".format(request.json["sender"])
            )
        db_receiver = User.query.filter_by(username=request.json["receiver"]).first()
        if db_receiver is None:
            return create_error_response(
                404, "Not found",
                "No user was found with the username {}".format(request.json["receiver"])
            )
        db_category_list = []
        for cat in request.json["category"]:
            db_category = Category.query.filter_by(categoryName=cat).first()
            if db_category is None:
                return create_error_response(
                    404, "Not found",
                    "No category was found with the categoryname(s) {}".format(request.json["category"])
                )
            db_category_list.append(db_category)
        

        transaction = Transaction(
            price=request.json["price"],
            dateTime=datetime.now(),
            sender=db_sender,
            receiver=db_receiver,
            category=db_category_list
 
        )

        try:
            db.session.add(transaction)
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "implement actual error message"
            )

        return Response(status=201, headers={
            "Location": url_for("api.transactionitem", transaction_id=transaction.id)
        })

class TransactionItem(Resource):
    def get(self, transaction_id):
        db_transaction = Transaction.query.filter_by(id=transaction_id).first()
        if db_transaction is None:
            return create_error_response(
                404, "Not found",
                "No transaction was found with the id {}".format(transaction_id)
            )

        body = TransactionBuilder(
            price=db_transaction.price,
            dateTime=str(db_transaction.dateTime),
            sender=db_transaction.sender.username,
            receiver=db_transaction.receiver.username,
            category=[cat.categoryName for cat in db_transaction.category]
            )
        body.add_namespace("bumeta", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.transactionitem", transaction_id=transaction_id))
        body.add_control("profile", TRANSACTION_PROFILE)
        body.add_control("bumeta:transactions-all", url_for("api.transactioncollection"))
        body.add_control_delete_transaction(transaction_id)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def delete(self, transaction_id):
        db_transaction = Transaction.query.filter_by(id=transaction_id).first()
        if db_transaction is None:
            return create_error_response(
                404, "Not found",
                "No transaction was found with the id {}".format(transaction_id)
            )

        db.session.delete(db_transaction)
        db.session.commit()

        return Response(status=204)
