from flask_restful import Resource

from flask import Flask, Response, request, url_for
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import IntegrityError

from jsonschema import validate, ValidationError
from budgethub import db
from budgethub.models import *
from budgethub.constants import *
from budgethub.utils import *

#User resources
class UserCollection(Resource):
    def get(self):
        body = UserBuilder()
        body.add_namespace("bumeta", LINK_RELATIONS_URL)
        body.add_control("self", "/api/users/")
        body.add_control_add_user()
        body.add_control_all_bank_accounts()
        body.add_control_all_categories()
        body.add_control_all_transactions()

        items = []
        for user in User.query.all():
            user_item_body = UserBuilder(
                username = user.username,
                bankAccount = [bankaccount.iban for bankaccount in user.bankAccount]

            )
            user_item_body.add_control("self", url_for("api.useritem", username=user.username))
            user_item_body.add_control("profile", USER_PROFILE)
            items.append(user_item_body)
        body["items"] = items

        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self):
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, UserBuilder.create_user_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        #TODO add bankaccount. i.e find bankaccount object from db
        #and link it to user.

        db_bankaccount_list = []
        for iban in request.json["bankAccount"]:
            db_bankaccount = BankAccount.query.filter_by(iban=iban).first()
            if db_bankaccount is None:
                return create_error_response(
                    404, "Not found",
                    "No bank account was found with the iban(s) {}".format(request.json["bankAccount"])
                )
            db_bankaccount_list.append(db_bankaccount)

        user = User(
            username=request.json["username"],
            password=request.json["password"],
            bankAccount=db_bankaccount_list
        )

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "User with name '{}' already exists.".format(request.json["username"])
            )

        return Response(status=201, headers={
            "Location": url_for("api.useritem", username=request.json["username"])
        })

class UserItem(Resource):
    def get(self, username):
        db_user = User.query.filter_by(username=username).first()
        if db_user is None:
            return create_error_response(
                404, "Not found",
                "No user was found with the username {}".format(username)
            )

        body = UserBuilder(
                username = db_user.username,
                bankAccount = [bankaccount.iban for bankaccount in db_user.bankAccount]
            )
        body.add_namespace("bumeta", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.useritem", username=username))
        body.add_control("profile", USER_PROFILE)
        body.add_control("bumeta:users-all", url_for("api.usercollection"))
        body.add_control_delete_user(username)
        body.add_control_edit_user(username)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, username):
        db_user = User.query.filter_by(username=username).first()
        if db_user is None:
            return create_error_response(
                404, "Not found",
                "No user was found with the username {}".format(username)
            )

        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, UserBuilder.create_user_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))


        for iban in request.json["bankAccount"]:
            db_bankaccount = BankAccount.query.filter_by(iban=iban).first()
            if db_bankaccount is None:
                return create_error_response(
                    404, "Not found",
                    "No bank account was found with the iban(s) {}".format(request.json["bankAccount"])
                )
            db_user.bankAccount.append(db_bankaccount)

        db_user.username = request.json["username"]
        db_user.password = request.json["password"]


        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return create_error_response(
                409, "Already exists",
                "User with username '{}' already exists.".format(request.json["username"])
            )

        return Response(status=204)

    def delete(self, username):
        db_user = User.query.filter_by(username=username).first()
        if db_user is None:
            return create_error_response(
                404, "Not found",
                "No user was found with the username {}".format(username)
            )

        db.session.delete(db_user)
        db.session.commit()

        return Response(status=204)
