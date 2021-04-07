import json
import os
import pytest
import tempfile
import time
from datetime import datetime
from jsonschema import validate
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

from budgethub import db, create_app
from budgethub.models import Transaction, BankAccount, User, Category

#development app
app = create_app()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def client():
    db_fd, db_fname = tempfile.mkstemp()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        populate_db()
        yield app.test_client()
        
    db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)

def _get_bankAccount(iban, bankName):
    return BankAccount(
        iban=iban,
        bankName=bankName
    )


def _get_user(username, password):
    return User(
        username=username,
        password=password
    )


def _get_category(name):
    return Category(
        categoryName=name
    )


def _get_transaction(price, dateTime, sender, receiver, category):
    return Transaction(
        price=price,
        dateTime=dateTime,
        sender=sender,
        receiver=receiver,
        category=category
    )

def populate_db():

    bankAccount1 = _get_bankAccount(iban="FI01", bankName="The bank")
    bankAccount2 = _get_bankAccount(iban="FI02", bankName="The bank")
    user1 = _get_user(username="user1", password="password")
    user2 = _get_user(username="user2", password="password2")
    user1.bankAccount.append(bankAccount1)
    user2.bankAccount.append(bankAccount2)
    category1 = _get_category(name="cat1")
    category2 = _get_category(name="cat2")
    transaction = _get_transaction(price=3.50, dateTime=datetime.now(), sender=user1, receiver=user2,
                                    category=[category1])

    db.session.add(bankAccount1)
    db.session.add(bankAccount2)
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(category1)
    db.session.add(category2)
    db.session.add(transaction)
    db.session.commit()
    
def _get_bankaccount_json(iban="FI03"):
    """
    Creates a valid bankaccount JSON object to be used for PUT and POST tests.
    """
    
    return {"iban":"{}".format(iban), "bankName":"The Bank", "user":["user1"]}
    
def _get_category_json(category_name="cat3"):
    '''
    Creates valid category json object to be used for put and post test
    '''
    
    return {"category_name":"{}".format(category_name), "transaction":["1"]}
    
def _check_namespace(client, response):
    """
    Checks that the "bumeta" namespace is found from the response body, and
    that its "name" attribute is a URL that can be accessed.
    """
    
    ns_href = response["@namespaces"]["bumeta"]["name"]
    resp = client.get(ns_href)
    assert resp.status_code == 200
    
def _check_control_get_method(ctrl, client, obj):
    """
    Checks a GET type control from a JSON object be it root document or an item
    in a collection. Also checks that the URL of the control can be accessed.
    """
    
    href = obj["@controls"][ctrl]["href"]
    resp = client.get(href)
    assert resp.status_code == 200
    
def _check_control_delete_method(ctrl, client, obj):
    """
    Checks a DELETE type control from a JSON object be it root document or an
    item in a collection. Checks the contrl's method in addition to its "href".
    Also checks that using the control results in the correct status code of 204.
    """
    
    href = obj["@controls"][ctrl]["href"]
    method = obj["@controls"][ctrl]["method"].lower()
    assert method == "delete"
    resp = client.delete(href)
    assert resp.status_code == 204
    
def _check_control_put_method(ctrl, client, obj):
    """
    Checks a PUT type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 204.
    """
    
    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "put"
    assert encoding == "json"
    body = _get_bankaccount_json()
    body["iban"] = obj["iban"]
    validate(body, schema)
    resp = client.put(href, json=body)
    assert resp.status_code == 204
    
def _check_category_control_put_method(ctrl, client, obj):
    """
    Checks a PUT type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 204.
    """
    
    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "put"
    assert encoding == "json"
    body = _get_bankaccount_json()
    body["category_name"] = obj["category_name"]
    validate(body, schema)
    resp = client.put(href, json=body)
    assert resp.status_code == 204
    
def _check_control_post_method(ctrl, client, obj):
    """
    Checks a POST type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 201.
    """
    
    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "post"
    assert encoding == "json"
    body = _get_bankaccount_json()
    validate(body, schema)
    resp = client.post(href, json=body)
    assert resp.status_code == 201
    
    
def _check_category_control_post_method(ctrl, client, obj):
    """
    Checks a POST type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 201.
    """
    
    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "post"
    assert encoding == "json"
    body = _get_category_json()
    validate(body, schema)
    resp = client.post(href, json=body)
    assert resp.status_code == 201

class TestBankaccountCollection(object):
    """
    This class implements tests for each HTTP method in Bankaccount collection
    resource. 
    """
    
    RESOURCE_URL = "/api/bankaccounts/"

    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """
        
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_post_method("bumeta:add-bank-account", client, body)
        assert len(body["items"]) == 2
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)
            assert "iban" in item
            assert "bankName" in item

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and 
        also checks that a valid request receives a 201 response with a 
        location header that leads into the newly created resource.
        """
        
        valid = _get_bankaccount_json()
        
        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + valid["iban"] + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["iban"] == "FI03"
        assert body["bankName"] == "The Bank"
        
        # send same data again for 409
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409
        
        # remove iban field for 400
        valid.pop("iban")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        
        
class TestSensorItem(object):
    
    RESOURCE_URL = "/api/bankaccounts/FI01/"
    INVALID_URL = "/api/bankaccounts/XD/"
    MODIFIED_URL = "/api/bankaccounts/FI03/"
    
    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["iban"] == "FI01"
        assert body["bankName"] == "The bank"
        _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("bumeta:banks-all", client, body)
        _check_control_put_method("edit", client, body)
        _check_control_delete_method("bumeta:delete", client, body)
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        """
        Tests the PUT method. Checks all of the possible erroe codes, and also
        checks that a valid request receives a 204 response. Also tests that
        when name is changed, the sensor can be found from a its new URI. 
        """
        
        valid = _get_bankaccount_json()
        
        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404
        
        # test with another bankaccounts iban 
        valid["iban"] = "FI02"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409
        
        '''# test with valid (only change model)
        valid["bankName"] = "New Bank"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204'''
        
        # remove field for 400
        valid.pop("bankName")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        
        valid = _get_bankaccount_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.MODIFIED_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["iban"] == valid["iban"]
        
    def test_delete(self, client):
        """
        Tests the DELETE method. Checks that a valid request reveives 204
        response and that trying to GET the sensor afterwards results in 404.
        Also checks that trying to delete a sensor that doesn't exist results
        in 404.
        """
        
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404
        
        
class TestCategoryCollection(object):
    """
    This class implements tests for each HTTP method in Bankaccount collection
    resource. 
    """
    
    RESOURCE_URL = "/api/categories/"

    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """
        
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_category_control_post_method("bumeta:add-category", client, body)
        assert len(body["items"]) == 2
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)
            assert "category_name" in item

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and 
        also checks that a valid request receives a 201 response with a 
        location header that leads into the newly created resource.
        """
        
        valid = _get_category_json()
        
        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + valid["category_name"] + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["category_name"] == "cat3"
        
        # send same data again for 409
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409
        
        # remove iban field for 400
        valid.pop("category_name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        
        
class TestCategoryItem(object):
    
    RESOURCE_URL = "/api/categories/cat1/"
    INVALID_URL = "/api/categories/XD/"
    MODIFIED_URL = "/api/categories/cat3/"
    
    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["category_name"] == "cat1"
        _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("bumeta:categories-all", client, body)
        _check_category_control_put_method("edit", client, body)
        _check_control_delete_method("bumeta:delete", client, body)
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        """
        Tests the PUT method. Checks all of the possible erroe codes, and also
        checks that a valid request receives a 204 response. Also tests that
        when name is changed, the sensor can be found from a its new URI. 
        """
        
        valid = _get_category_json()
        
        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 400
        
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404
        
        # test with another bankaccounts iban 
        valid["category_name"] = "cat2"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409
        
        '''# test with valid (only change model)
        valid["category_name"] = "cat5"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204'''
        
        # remove field for 415 because no body
        valid.pop("category_name")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        
        valid = _get_category_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.MODIFIED_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["category_name"] == valid["category_name"]
        
    def test_delete(self, client):
        """
        Tests the DELETE method. Checks that a valid request reveives 204
        response and that trying to GET the sensor afterwards results in 404.
        Also checks that trying to delete a sensor that doesn't exist results
        in 404.
        """
        
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404
