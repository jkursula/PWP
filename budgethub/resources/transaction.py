from flask_restful import Resource

from flask import Flask, Response, request, url_for
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import IntegrityError

from budgethub import db
from budgethub.models import *
from budgethub.constants import *
from budgethub.utils import *

from datetime import datetime

#Transaction resources
class TransactionCollection(Resource):
    def get(self):
        body = TransactionBuilder()
        body.add_namespace("bumeta", LINK_RELATIONS_URL)
        body.add_control("self", "/api/users/")
        body.add_control_add_transaction()

        items = []
        for transaction in Transaction.query.all():
            transaction_item_body = TransactionBuilder(
                id = transaction.id,
                price = transaction.price,
                dateTime = transaction.dateTime,
                sender = transaction.sender,
                receiver = transaction.receiver,
                category = transaction.category
            )
            transaction_item_body.add_control("self", url_for("api.transactionitem", id=transaction.id))
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

        #TODO add bankaccount. i.e find bankaccount object from db
        #and link it to user.
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d")

        transaction = Transaction(
            price=request.json["price"],
            dateTime=datetime.now(),
            sender=request.json["sender"],
            receiver=request.json["receiver"],
            category=request.json["category"]
 
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
            "Transaction created"
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
            dateTime=db_transaction.dateTime,
            sender=db_transaction.sender,
            receiver=db_transaction.receiver,
            category=db_transaction.category
            )
        body.add_namespace("bumeta", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.transactionitem", id=transaction_id))
        body.add_control("profile", TRANSACTION_PROFILE)
        body.add_control("bumeta:transactions-all", url_for("api.transactioncollection"))
        body.add_control_delete_transaction(db_transaction)

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