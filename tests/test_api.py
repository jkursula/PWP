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
import tests.utils as utils


'''

Modified from the example in the course exercises from 
https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/testing-flask-applications-part-2/

'''
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

#Function for populating database with above items
def populate_db():

    bankAccount1 = utils._get_bankAccount(iban="FI01", bankName="The bank")
    bankAccount2 = utils._get_bankAccount(iban="FI02", bankName="The bank")
    user1 = utils._get_user(username="user1", password="password")
    user2 = utils._get_user(username="user2", password="password2")
    user1.bankAccount.append(bankAccount1)
    user2.bankAccount.append(bankAccount2)
    category1 = utils._get_category(name="cat1")
    category2 = utils._get_category(name="cat2")
    transaction = utils._get_transaction(price=3.50, dateTime=datetime.now(), sender=user1, receiver=user2,
                                    category=[category1])

    db.session.add(bankAccount1)
    db.session.add(bankAccount2)
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(category1)
    db.session.add(category2)
    db.session.add(transaction)
    db.session.commit()

    
class TestEntryPoint(object):

    #Test that the api's entry point is accessible
    # and also checks that all the controls are working correctly
    
    RESOURCE_URL = "/api/"
    
    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        utils._check_namespace(client, body)
        assert len(body["@controls"]) == 4
        utils._check_control_get_method("bumeta:transactions-all", client, body)
        utils._check_control_get_method("bumeta:users-all", client, body)
        utils._check_control_get_method("bumeta:bankaccounts-all", client, body)
        utils._check_control_get_method("bumeta:categories-all", client, body)

class TestAdminSite(object):

#Test that the Api's admin site or client is accessible

    RESOURCE_URL = "/admin/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
    
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
        utils._check_namespace(client, body)
        utils._check_control_post_method("bumeta:add-bank-account", client, body)
        utils._check_control_get_method("bumeta:categories-all", client, body)
        utils._check_control_get_method("bumeta:transactions-all", client, body)
        utils._check_control_get_method("bumeta:users-all", client, body)
        assert len(body["items"]) == 2
        for item in body["items"]:
            utils._check_control_get_method("self", client, item)
            utils._check_control_get_method("profile", client, item)
            assert "iban" in item
            assert "bankName" in item

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and 
        also checks that a valid request receives a 201 response with a 
        location header that leads into the newly created resource.
        """
        
        valid = utils._get_bankaccount_json()
        
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
        
        
class TestBankaccountItem(object):
    
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
        utils._check_namespace(client, body)
        utils._check_control_get_method("profile", client, body)
        utils._check_control_get_method("bumeta:bank-accounts-all", client, body)
        utils._check_control_put_method("edit", client, body)
        utils._check_control_delete_method("bumeta:delete", client, body)
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        """
        Tests the PUT method. Checks all of the possible erroe codes, and also
        checks that a valid request receives a 204 response. Also tests that
        when name is changed, the bankaccount can be found from a its new URI. 
        """
        
        valid = utils._get_bankaccount_json()
        validmod = utils._get_modified_bankaccount_json()
        
        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404
        
        # test with another bankaccounts iban 
        valid["iban"] = "FI02"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409
        
        # test with valid (only change model)
        validmod["bankName"] = "New Bank"
        resp = client.put(self.RESOURCE_URL, json=validmod)
        assert resp.status_code == 204
        
        # remove field for 400
        valid.pop("bankName")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        
        valid = utils._get_bankaccount_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.MODIFIED_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["iban"] == valid["iban"]
        
    def test_delete(self, client):
        """
        Tests the DELETE method. Checks that a valid request reveives 204
        response and that trying to GET the bankaccount afterwards results in 404.
        Also checks that trying to delete a bankaccount that doesn't exist results
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
    This class implements tests for each HTTP method in Category collection
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
        utils._check_namespace(client, body)
        utils._check_category_control_post_method("bumeta:add-category", client, body)
        utils._check_control_get_method("bumeta:bank-accounts-all", client, body)
        utils._check_control_get_method("bumeta:transactions-all", client, body)
        utils._check_control_get_method("bumeta:users-all", client, body)
        assert len(body["items"]) == 2
        for item in body["items"]:
            utils._check_control_get_method("self", client, item)
            utils._check_control_get_method("profile", client, item)
            assert "category_name" in item

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and 
        also checks that a valid request receives a 201 response with a 
        location header that leads into the newly created resource.
        """
        
        valid = utils._get_category_json()
        
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
        
        # remove category_name field for 400
        valid.pop("category_name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        
        
class TestCategoryItem(object):
    
    RESOURCE_URL = "/api/categories/cat1/"
    INVALID_URL = "/api/categories/XD/"
    MODIFIED_URL = "/api/categories/cat50/"
    
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
        utils._check_namespace(client, body)
        utils._check_control_get_method("profile", client, body)
        utils._check_control_get_method("bumeta:categories-all", client, body)
        utils._check_category_control_put_method("edit", client, body)
        utils._check_control_delete_method("bumeta:delete", client, body)
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        """
        Tests the PUT method. Checks all of the possible error codes, and also
        checks that a valid request receives a 204 response. Also tests that
        when name is changed, the category can be found from a its new URI. 
        """
        
        valid = utils._get_category_json()
        
        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 400
        
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404
        
        # test with another category's name 
        valid["category_name"] = "cat2"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409
        
        
        # test with valid (only change model)
        valid["category_name"] = "cat50"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204
        
        # remove field not possible because no body after it
        '''valid.pop("category_name")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400'''
        
        validmod = utils._get_modified_category_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.MODIFIED_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["category_name"] == validmod["category_name"]
        
    def test_delete(self, client):
        """
        Tests the DELETE method. Checks that a valid request reveives 204
        response and that trying to GET the category afterwards results in 404.
        Also checks that trying to delete a category that doesn't exist results
        in 404.
        """
        
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404
        
class TestUserCollection(object):
    """
    This class implements tests for each HTTP method in User collection
    resource. 
    """
    
    RESOURCE_URL = "/api/users/"

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
        utils._check_namespace(client, body)
        utils._check_user_control_post_method("bumeta:add-user", client, body)
        utils._check_control_get_method("bumeta:bank-accounts-all", client, body)
        utils._check_control_get_method("bumeta:transactions-all", client, body)
        utils._check_control_get_method("bumeta:categories-all", client, body)
        assert len(body["items"]) == 2
        for item in body["items"]:
            utils._check_control_get_method("self", client, item)
            utils._check_control_get_method("profile", client, item)
            assert "username" in item
            #assert "password" in item

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and 
        also checks that a valid request receives a 201 response with a 
        location header that leads into the newly created resource.
        """
        
        valid = utils._get_user_json()
        wrong_bank = {"username": "user10","password": "Kakka","bankAccount": ["en kerros"]}
        resp = client.post(self.RESOURCE_URL, json=wrong_bank)
        assert resp.status_code == 404
        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + valid["username"] + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["username"] == "user3"
        assert body["bankAccount"] == ["FI01"]
        
        # send same data again for 409
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        #remove bankAccount fiel for 400
        valid.pop("bankAccount")
        print(valid)
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        # remove username field for 400
        valid.pop("username")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        
        
class TestUserItem(object):
    
    RESOURCE_URL = "/api/users/user1/"
    INVALID_URL = "/api/users/XD/"
    MODIFIED_URL = "/api/users/user3/"
    
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
        assert body["username"] == "user1"
        assert body["bankAccount"] == ["FI01"]
        utils._check_namespace(client, body)
        utils._check_control_get_method("profile", client, body)
        utils._check_control_get_method("bumeta:users-all", client, body)
        utils._check_user_control_put_method("edit", client, body)
        utils._check_control_delete_method("bumeta:delete", client, body)
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        """
        Tests the PUT method. Checks all of the possible erroe codes, and also
        checks that a valid request receives a 204 response. Also tests that
        when name is changed, the user can be found from a its new URI. 
        """
        
        valid = utils._get_user_json()
        validmod = utils._get_modified_user_json()
        wrong_bank = {"username": "user1","password": "Kakka","bankAccount": ["en kerros"]}
        resp = client.put(self.RESOURCE_URL, json=wrong_bank)
        assert resp.status_code == 404

        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404
        
        # test with another users username 
        valid["username"] = "user2"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409
        
        # test with valid (only change model)
        validmod["password"] = "kerronpas"
        resp = client.put(self.RESOURCE_URL, json=validmod)
        assert resp.status_code == 204
        
        # remove field for 400
        valid.pop("username")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        
        valid = utils._get_user_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.MODIFIED_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["username"] == valid["username"]
        
    def test_delete(self, client):
        """
        Tests the DELETE method. Checks that a valid request reveives 204
        response and that trying to GET the user afterwards results in 404.
        Also checks that trying to delete a user that doesn't exist results
        in 404.
        """
        
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404
       
class TestTransactionCollection(object):
    """
    This class implements tests for each HTTP method in Transaction collection
    resource. 
    """
    
    RESOURCE_URL = "/api/transactions/"
    DELETE_USER1_URL = "/api/users/user1/"
    DELETE_USER2_URL = "/api/users/user2/"

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
        utils._check_namespace(client, body)
        utils._check_transaction_control_post_method("bumeta:add-transaction", client, body)
        utils._check_control_get_method("bumeta:bank-accounts-all", client, body)
        utils._check_control_get_method("bumeta:categories-all", client, body)
        utils._check_control_get_method("bumeta:users-all", client, body)
        assert len(body["items"]) == 1
        for item in body["items"]:
            utils._check_control_get_method("self", client, item)
            utils._check_control_get_method("profile", client, item)
            assert "id" in item
            assert "price" in item
            assert "dateTime" in item
            assert "sender" in item
            assert "receiver" in item
            assert "category" in item
        client.delete(self.DELETE_USER1_URL)
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        client.delete(self.DELETE_USER2_URL)
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200

            

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and 
        also checks that a valid request receives a 201 response with a 
        location header that leads into the newly created resource.
        """
        
        valid = utils._get_transaction_json()
        print(valid)
        wrong_user = "vaarin"
        wrong_user2 = "xd"
        wrong_category = ["cat666"]
        
        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["sender"] == "user1"
        
        #test that wrong users or categories cannot be used
        valid["category"] = wrong_category
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 404
        valid = utils._get_transaction_json()
        valid["sender"] = wrong_user
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 404
        valid = utils._get_transaction_json()
        valid["receiver"] = wrong_user2
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 404

        #remove receiver field to test that it fails
        valid.pop("receiver")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        # remove price field for 400
        valid.pop("price")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        
        
class TestTransactionItem(object):
    
    RESOURCE_URL = "/api/transactions/1/"
    INVALID_URL = "/api/transactions/5/"
    MODIFIED_URL = "/api/transactions/3/"
    DELETE_USER1_URL = "/api/users/user1/"
    DELETE_USER2_URL = "/api/users/user2/"
    
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
        assert body["receiver"] == "user2"
        assert body["sender"] == "user1"
        utils._check_namespace(client, body)
        utils._check_control_get_method("profile", client, body)
        utils._check_control_get_method("bumeta:transactions-all", client, body)
        client.delete(self.DELETE_USER1_URL)
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        client.delete(self.DELETE_USER2_URL)
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        #_check_transaction_control_put_method("edit", client, body)
        utils._check_control_delete_method("bumeta:delete", client, body)
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    '''
    put not implemented
    def test_put(self, client):
        """
        Tests the PUT method. Checks all of the possible erroe codes, and also
        checks that a valid request receives a 204 response. Also tests that
        when name is changed, the transaction can be found from a its new URI. 
        """
        
        valid = _get_transaction_json()
        
        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404
        
        # test with another transactions sender 
        valid["username"] = "user2"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409
        
        # test with valid (only change model)
        valid["password"] = "New password"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204
        
        # remove field for 400
        valid.pop("username")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        
        valid = _get_user_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.MODIFIED_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["username"] == valid["username"]'''

    def test_delete(self, client):
        """
        Tests the DELETE method. Checks that a valid request reveives 204
        response and that trying to GET the transaction afterwards results in 404.
        Also checks that trying to delete a transaction that doesn't exist results
        in 404.
        """
        
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404        
