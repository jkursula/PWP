import os
import json
from flask import Flask, Response
from flask_sqlalchemy import SQLAlchemy
from budgethub.constants import *

db = SQLAlchemy()

# Based on http://flask.pocoo.org/docs/1.0/tutorial/factory/#the-application-factory
# Modified to use Flask SQLAlchemy
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "development.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    from . import models
    from . import api
    app.cli.add_command(models.init_db_command)
    # app.cli.add_command(models.generate_test_data)
    app.register_blueprint(api.api_bp)

    @app.route(LINK_RELATIONS_URL)
    def send_link_relations():
        return "link relations"

    @app.route("/profiles/<profile>/")
    def send_profile(profile):
        return "you requests {} profile".format(profile)
    
    @app.route("/api/")
    def entry():
        body = utils.MasonBuilder()
        body.add_namespace("bumeta", "/bumeta/link-relations/")
        body.add_control("bumeta:transactions-all", "/api/transactions/", method="GET")
        body.add_control("bumeta:users-all", "/api/users/", method="GET")
        body.add_control("bumeta:bankaccounts-all", "/api/bankaccounts/", method="GET")
        body.add_control("bumeta:categories-all", "/api/categories/", method="GET")
        return Response(json.dumps(body), 200, mimetype=MASON)

    # @app.route("/admin/")
    # def admin_site():
    #     return app.send_static_file("html/admin.html")

    return app
