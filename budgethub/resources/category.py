from flask_restful import Resource

from flask import Flask, Response, request, url_for
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import IntegrityError

from budgethub import db
from budgethub.models import *
from budgethub.constants import *
from budgethub.utils import *


# Category resources
class CategoryCollection(Resource):
    def get(self):
        body = CategoryBuilder()
        body.add_namespace("bumeta", LINK_RELATIONS_URL)
        body.add_control_add_category()

        categories = []
        for category in Categories.query.all():
            category_body = CategoryBuilder(
                categoryName=category.categoryName
            )
            category_body.add_control("self", url_for(
                "api.categoryitem", description=category.description))
            category_body.add_control("profile", CATEGORY_PROFILE)
            categories.append(category_body)
        body["items"] = categories

        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self):
        if not request.json:
            return create_error_response(
                415, "Unsupported media type", "Requests must be JSON")
        try:
            validate(request.json, CategoryBuilder.category_schema())
        except ValidationError:
            return create_error_response(
                400, "Invalid JSON document", str(ValidationError)
            )

        category = Cateory(
            categoryName=request.json["categoryName"]
        )

        try:
            db.session.add(category)
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Category with name {} already exists.".format(
                    request.json["categoryName"]
                )
            )
        return Rsponse(status=201, headers={
            "Location": url_for(
                "api.categoryitem", categoryName=request.json["categoryName"])
        })


class CategoryItem(Resource):
    def get(self, category_name):
        db_category = Category.query.filter_by(
            category_name=category_name.first()
        )
        if db_category is None:
            return create_error_response(
                404, "Not found",
                "No category was foung with a name {}.".format(category_name)
            )

        body = Category(
            categoryName=db_category.category_name
        )

        body.add_namespace("bumeta", LINK_RELATIONS_URL)
        body.add_control(
            "self", url_for("api.categoryitem", categoryName=category_name))
        body.add_control("profile", CATEGORY_PROFILE)
        body.add_control(
            "bumeta:categories-all", url_for("api.categorycollection"))
        body.add_control_delete_category(category_name)
        body.add_control_edit_category(category_name)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, category_name):
        db_category = Category.query.filter_by(
            categoryName=category_name).first()
        if db_category is None:
            return create_error_response(
                404, "Not found", "Requests must be JSON"
            )

        try:
            validate(request.json, CategoryBuilder.category_schema())
        except ValidationError:
            return create_error_response(
                400, "Invalid JSON document", str(ValidationError))

        db_category.category_name = request.json["categoryName"]

        try:
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Category with name {} already exists.".format(category_name)
            )

        return Response(status=204)

    def delete(self, category_name):
        db_category = Category.query.filter_by(
            categoryName=category_name).first()
        if db_category is None:
            return create_error_response(
                404, "Not found",
                "No category was found with a name '{}'.".format(category_name)
            )

        db.session.delete(db_category)
        db.session.commit()

        return Response(status=204)