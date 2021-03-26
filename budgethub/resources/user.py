from flask_restful import Resource

from flask import Flask, Response, request, url_for
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import IntegrityError

from budgethub import db
from budgethub.models import *
from budgethub.constants import *
from budgethub.utils import *

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