from jsonschema import validate
from budgethub.models import Transaction, BankAccount, User, Category

#Creates bankaccount database item    
def _get_bankAccount(iban, bankName):
    return BankAccount(
        iban=iban,
        bankName=bankName
    )

#creates user database item
def _get_user(username, password):
    return User(
        username=username,
        password=password
    )

#Creates category database item
def _get_category(name):
    return Category(
        categoryName=name
    )

#Creates transaction database item
def _get_transaction(price, dateTime, sender, receiver, category):
    return Transaction(
        price=price,
        dateTime=dateTime,
        sender=sender,
        receiver=receiver,
        category=category
    )

def _get_bankaccount_json(iban="FI03"):
    """
    Creates a valid bankaccount JSON object to be used for POST tests.
    """
    
    return {"iban":"{}".format(iban), "bankName":"The Bank", "user":["user1"]}
    
def _get_modified_bankaccount_json(iban="FI01"):
    """
    Creates a valid bankaccount JSON object to be used for PUT  tests.
    """
    
    return {"iban":"{}".format(iban), "bankName":"The Bank", "user":["user1"]}
    
def _get_category_json(category_name="cat3"):
    '''
    Creates valid category json object to be used for post test
    '''
    
    return {"category_name":"{}".format(category_name), "transaction":["1"]}
    
def _get_modified_category_json(category_name="cat50"):
    '''
    Creates valid category json object to be used for put test
    '''
    
    return {"category_name":"{}".format(category_name), "transaction":["1"]}
 

def _get_user_json(username="user3"):
    """
    Creates a valid user JSON object to be used for POST tests.
    """
    
    return {"username":"{}".format(username), "password":"En kerro", "bankAccount":["FI01"]}
    
def _get_modified_user_json(username="user1"):
    """
    Creates a valid user JSON object to be used for PUT tests.
    """
    
    return {"username":"{}".format(username), "password":"test", "bankAccount":["FI01"]}
    
def _get_transaction_json():
    """
    Creates a valid bankaccount JSON object to be used for POST tests.
    """
    
    return {"price":10.63, "datetime":"2020-10-10", "sender":"user1", "receiver":"user2", "category":["cat1"]}

    
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

def _check_user_control_put_method(ctrl, client, obj):
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
    body = _get_user_json()
    body["username"] = obj["username"]
    validate(body, schema)
    resp = client.put(href, json=body)
    assert resp.status_code == 204
    
''' Not implemented for transaction
def _check_transaction_control_put_method(ctrl, client, obj):
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
    body = _get_transaction_json()
    body["id"] = obj["id"]
    validate(body, schema)
    resp = client.put(href, json=body)
    assert resp.status_code == 204'''
    
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
    
def _check_user_control_post_method(ctrl, client, obj):
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
    body = _get_user_json()
    validate(body, schema)
    resp = client.post(href, json=body)
    assert resp.status_code == 201
    
def _check_transaction_control_post_method(ctrl, client, obj):
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
    body = _get_transaction_json()
    validate(body, schema)
    resp = client.post(href, json=body)
    assert resp.status_code == 201