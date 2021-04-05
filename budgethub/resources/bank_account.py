from flask_restful import Resource

from flask import Flask, Response, request, url_for
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import IntegrityError
from jsonschema import validate, ValidationError
from budgethub import db
from budgethub.models import *
from budgethub.constants import *
from budgethub.utils import *

#Bank account resources
class BankAccountCollection(Resource):
    def get(self):
        body = BankAccountBuilder()
        body.add_namespace("bumeta", LINK_RELATIONS_URL)
        body.add_control("self", "/api/bankaccounts/")
        body.add_control_add_bank_account()

        banks = []
        for bank in BankAccount.query.all():
            bank_item_body = BankAccountBuilder(
                iban = bank.iban,
                bankName = bank.bankName

            )
            bank_item_body.add_control("self", url_for("api.bankaccountitem", bankaccount_id=bank.iban))
            bank_item_body.add_control("profile", BANK_ACCOUNT_PROFILE)
            banks.append(bank_item_body)
        body["items"] = banks

        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self):
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, BankAccountBuilder.bank_account_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        bank = BankAccount(
            iban=request.json["iban"],
            bankName=request.json["bankName"]
 
        )

        try:
            db.session.add(bank)
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Bankaccount with iban '{}' already exists.".format(request.json["iban"])
            )

        return Response(status=201, headers={
            "Location": url_for("api.bankaccountitem", bankaccount_id=request.json["iban"])
        })

class BankAccountItem(Resource):
    def get(self, bankaccount_id):
        db_bank = BankAccount.query.filter_by(iban=bankaccount_id).first()
        if db_bank is None:
            return create_error_response(
                404, "Not found",
                "No Bankaccount was found with the iban {}".format(bankaccount_id)
            )

        body = BankAccountBuilder(
                iban = db_bank.iban,
                bankName = db_bank.bankName
            )
        body.add_namespace("bumeta", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.bankaccountitem", bankaccount_id=bankaccount_id))
        body.add_control("profile", BANK_ACCOUNT_PROFILE)
        body.add_control("bumeta:banks-all", url_for("api.bankaccountcollection"))
        body.add_control_delete_bank_account(bankaccount_id)
        body.add_control_edit_bank_account(bankaccount_id)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, bankaccount_id):
        db_bank = BankAccount.query.filter_by(iban=bankaccount_id).first()
        if db_bank is None:
            return create_error_response(
                404, "Not found",
                "No bankaccount was found with the iban {}".format(bankaccount_id)
            )

        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, BankAccountBuilder.bank_account_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        db_bank.iban = request.json["iban"]
        db_bank.bankName = request.json["bankName"]

        try:
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Bankaccount with iban '{}' already exists.".format(request.json["iban"])
            )

        return Response(status=204)

    def delete(self, bankaccount_id):
        db_bank = BankAccount.query.filter_by(iban=bankaccount_id).first()
        if db_bank is None:
            return create_error_response(
                404, "Not found",
                "No Bankaccount was found with the iban {}".format(bankaccount_id)
            )

        db.session.delete(db_bank)
        db.session.commit()

        return Response(status=204)
