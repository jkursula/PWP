//modified from excercises and from https://github.com/enkwolf/pwp-course-sensorhub-api-example/
"use strict"; 
const DEBUG = true;
const MASONJSON = "application/vnd.mason+json";
const PLAINJSON = "application/json";

//renders error message in case something fails
function renderError(jqxhr) {
    let msg = jqxhr.responseJSON["@error"]["@message"];
    $("div.notification").html("<p class='error'>" + msg + "</p>");
}

//renders messages to be displayed about the programs functions
function renderMsg(msg) {
    $("div.notification").html("<p class='msg'>" + msg + "</p>");
}

//sends get request to url and calls for function renderer
function getResource(href, renderer) {
    $.ajax({
        url: href,
        success: renderer,
        error: renderError
    });
}

//used for sending data with POST and PUT methods
function sendData(href, method, item, postProcessor) {
    console.log("Test " + href)
    $.ajax({
        url: href,
        type: method,
        data: JSON.stringify(item),
        contentType: PLAINJSON,
        processData: false,
        success: postProcessor,
        error: renderError
    });
}

//Used for deletion of items
function deleteData(href, postProcessor) {
$.ajax({
    url: href,
    type: "DELETE",
    success: postProcessor,
    error: renderError
});
}

//puts data for table elements for transaction collection and item
function transactionsRow(item) {
    let link = "<a href='" +
                item["@controls"].self.href +
                "' onClick='followLink(event, this, renderTransaction)'>Edit</a>";

    return "<tr><td>" + item.price +
            "</td><td>" + item.dateTime +
            "</td><td>" + item.sender +
            "</td><td>" + item.receiver +
            "</td><td>" + item.category +
            "</td><td>" + link + "</td></tr>";
} 

//puts data for table elements for users collection and item
function usersRow(item) {
    let link = "<a href='" +
                item["@controls"].self.href +
                "' onClick='followLink(event, this, renderUser)'>Edit</a>";

    return "<tr><td>" + item.username +
            "</td><td>" + item.bankAccount + 
            "</td><td>" + link + "</td></tr>";
}
//puts data for table elements for bankaccount collection and item
function bankAccountsRow(item) {
    let link = "<a href='" +
                item["@controls"].self.href +
                "' onClick='followLink(event, this, renderBankAccount)'>Edit</a>";

    return "<tr><td>" + item.iban +
            "</td><td>" + item.bankName +
            "</td><td>" + item.user + 
            "</td><td>" + link + "</td></tr>";
}

//puts data for table elements in category collection and item
function categoriesRow(item) {
    let link = "<a href='" +
                item["@controls"].self.href +
                "' onClick='followLink(event, this, renderCategory)'>Edit</a>";

    return "<tr><td>" + item.category_name +
            "</td><td>" + item.transaction + 
            "</td><td>" + link + "</td></tr>";
}
//Not in use
function transactionRow(item) {

    return "<tr><td>" + item.price +
            "</td><td>" + item.sender + "</td></tr>";
}

//Not in use
function userRow(item) {

    return "<tr><td>" + item.username +
            "</td><td>" + item.bankAccount + "</td></tr>";
}

//Not in use
function bankAccountRow(item) {

    return "<tr><td>" + item.iban +
            "</td><td>" + item.bankName + "</td></tr>";
}

//Not in use
function categoryRow(item) {

    return "<tr><td>" + item.category_name + "</td></tr>";
}
//Adds new elements after submitting or editing
function appendTransactionRow(body) {
    $(".resulttable tbody").append(transactionsRow(body));
}

//Adds new elements after submitting or editing
function appendUserRow(body) {
    $(".resulttable tbody").append(usersRow(body));
}

//Adds new elements after submitting or editing
function appendBankAccountRow(body) {
    $(".resulttable tbody").append(bankAccountsRow(body));
}

//Adds new elements after submitting or editing
function appendCategoryRow(body) {
    $(".resulttable tbody").append(categoriesRow(body));
}

//Gets transaction after its creation to make sure it actually exists
function getSubmittedTransaction(data, status, jqxhr) {
    renderMsg("Successful");
    let href = jqxhr.getResponseHeader("Location");
    if (href) {
        getResource(href, appendTransactionRow);
    }
}

//Gets user after its creation to make sure it actually exists
function getSubmittedUser(data, status, jqxhr) {
    renderMsg("Successful");
    let href = jqxhr.getResponseHeader("Location");
    if (href) {
        getResource(href, appendUserRow);
    }
}

//Gets bank account after its creation to make sure it actually exists
function getSubmittedBankAccount(data, status, jqxhr) {
    renderMsg("Successful");
    let href = jqxhr.getResponseHeader("Location");
    if (href) {
        getResource(href, appendBankAccountRow);
    }
}

//Gets category after its creation to make sure it actually exists
function getSubmittedCategory(data, status, jqxhr) {
    renderMsg("Successful");
    let href = jqxhr.getResponseHeader("Location");
    if (href) {
        getResource(href, appendCategoryRow);
    }
}

//used for link navigation
function followLink(event, a, renderer) {
    event.preventDefault();
    getResource($(a).attr("href"), renderer);
}

//Handles submission of new transaction or editing
function submitTransaction(event) {
    event.preventDefault();

    let data = {};
    let form = $("div.form form");
    data.price = parseFloat($("input[name='price']").val());
    data.sender = $("input[name='sender']").val();
    data.receiver = $("input[name='receiver']").val();
    data.category = $("input[name='category']").val().split(",");
    sendData(form.attr("action"), form.attr("method"), data, getSubmittedTransaction);
}

//Handles submission of new user or editing
function submitUser(event) {
    event.preventDefault();

    let data = {};
    let form = $("div.form form");
    data.username = $("input[name='username']").val();
    data.password = $("input[name='password']").val();
    data.bankAccount = $("input[name='bankAccount']").val().split(",");
    sendData(form.attr("action"), form.attr("method"), data, getSubmittedUser);
}
//Handles submission of new bankaccount or editing
function submitBankAccount(event) {
    event.preventDefault();

    let data = {};
    let form = $("div.form form");
    data.iban = $("input[name='iban']").val();
    data.bankName = $("input[name='bankName']").val();
    sendData(form.attr("action"), form.attr("method"), data, getSubmittedBankAccount);
}

//handles submission of new category or editing
function submitCategory(event) {
    event.preventDefault();

    let data = {};
    let form = $("div.form form");
    data.category_name = $("input[name='category_name']").val();
    sendData(form.attr("action"), form.attr("method"), data, getSubmittedCategory);
}

//Handles the rendering of the form elements for transaction 
function renderTransactionForm(ctrl) {
    let form = $("<form>");
    let price = ctrl.schema.properties.price;
    let receiver = ctrl.schema.properties.receiver;
    let sender = ctrl.schema.properties.sender;
    let category = ctrl.schema.properties.category;
    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.submit(submitTransaction);
    form.append("<label>" + price.description + "</label>");
    form.append("<input type='number' name='price'>");
    form.append("<label>" + receiver.description + "</label>");
    form.append("<input type='text' name='receiver'>");
    form.append("<label>" + sender.description + "</label>");
    form.append("<input type='text' name='sender'>");
    form.append("<label>" + category.description + "</label>");
    form.append("<input type='array' name='category'>");
    ctrl.schema.required.forEach(function (property) {
        $("input[name='" + property + "']").attr("required", true);
    });
    form.append("<input type='submit' name='submit' value='Submit'>");
    $("div.form").html(form);
}

//handles rendering of user form for user 
function renderUserForm(ctrl) {
    let form = $("<form>");
    let username = ctrl.schema.properties.username;
    let password = ctrl.schema.properties.password;
    let bankAccount = ctrl.schema.properties.bankAccount;
    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.submit(submitUser);
    form.append("<label>" + username.description + "</label>");
    form.append("<input type='text' name='username'>");
    form.append("<label>" + password.description + "</label>");
    form.append("<input type='text' name='password'>");
    form.append("<label>" + bankAccount.description + "</label>");
    form.append("<input type='array' name='bankAccount'>");
    ctrl.schema.required.forEach(function (property) {
        $("input[name='" + property + "']").attr("required", true);
    });
    form.append("<input type='submit' name='submit' value='Submit'>");
    $("div.form").html(form);
}

//handles rendering of form for bank account 
function renderBankAccountForm(ctrl) {
    let form = $("<form>");
    let iban = ctrl.schema.properties.iban;
    let bankName = ctrl.schema.properties.bankName;
    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.submit(submitBankAccount);
    form.append("<label>" + iban.description + "</label>");
    form.append("<input type='text' name='iban'>");
    form.append("<label>" + bankName.description + "</label>");
    form.append("<input type='text' name='bankName'>");
    ctrl.schema.required.forEach(function (property) {
        $("input[name='" + property + "']").attr("required", true);
    });
    form.append("<input type='submit' name='submit' value='Submit'>");
    $("div.form").html(form);
}

//handles rendering of form elements for category
function renderCategoryForm(ctrl) {
    let form = $("<form>");
    let category_name = ctrl.schema.properties.category_name;
    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.submit(submitCategory);
    form.append("<label>" + category_name.description + "</label>");
    form.append("<input type='text' name='category_name'>");
    ctrl.schema.required.forEach(function (property) {
        $("input[name='" + property + "']").attr("required", true);
    });
    form.append("<input type='submit' name='submit' value='Submit'>");
    $("div.form").html(form);
}

//renders view for transaction item
function renderTransaction(body) {
    $("div.navigation").html(
        "<a href='" +
        body["@controls"]["bumeta:transactions-all"].href +
        "' onClick='followLink(event, this, renderTransactions)'>Transaction Collection</a>"
    );
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    $("div.notification").empty();
    $("input[name='price']").val(body.price);
    $("input[name='dateTime']").val(body.dateTime);
    $("input[name='sender']").val(body.sender);
    $("input[name='receiver']").val(body.receiver);
    $("input[name='category']").val(body.category);
    $("div.deletebutton").html("<button onClick='deleteData(\""+body["@controls"]["bumeta:delete"].href+"\"); renderMsg(\"Deleted\");'>DELETE</button>");
}

//render view for user item
function renderUser(body) {
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    $("div.notification").empty();
    $("div.navigation").html(
        "<a href='" +
        body["@controls"]["bumeta:users-all"].href +
        "' onClick='followLink(event, this, renderUsers)'>Users Collection</a>"
    );
    renderUserForm(body["@controls"].edit);
    $("input[name='username']").val(body.username);
    $("input[name='bankAccount']").val(body.bankAccount);
    $("div.deletebutton").html("<button onClick='deleteData(\""+body["@controls"]["bumeta:delete"].href+"\"); renderMsg(\"Deleted\");'>DELETE</button>");
}

//renders view for bank account item
function renderBankAccount(body) {
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    $("div.notification").empty();
    $("div.navigation").html(
        "<a href='" +
        body["@controls"]["bumeta:banks-all"].href +
        "' onClick='followLink(event, this, renderBankAccounts)'>Bank Account Collection</a>"
    );
    renderBankAccountForm(body["@controls"].edit);
    $("input[name='iban']").val(body.iban);
    $("input[name='bankName']").val(body.bankName);
    $("input[name='user']").val(body.user);
    $("div.deletebutton").html("<button onClick='deleteData(\""+body["@controls"]["bumeta:delete"].href+"\"); renderMsg(\"Deleted\");'>DELETE</button>");
}

//renders view for category item
function renderCategory(body) {
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    $("div.notification").empty();
    $("div.navigation").html(
        "<a href='" +
        body["@controls"]["bumeta:categories-all"].href +
        "' onClick='followLink(event, this, renderCategories)'>Category Collection</a>"
    );
    renderCategoryForm(body["@controls"].edit);
    $("input[name='category_name']").val(body.category_name);
    $("div.deletebutton").html("<button onClick='deleteData(\""+body["@controls"]["bumeta:delete"].href+"\"); renderMsg(\"Deleted\");'>DELETE</button>");
}

//handles rendering of transaction collection view
function renderTransactions(body) {
    $("div.navigation").empty();
    $("div.deletebutton").empty();
    $("div.notification").empty();
    $("div.tablecontrols").empty();
    $(".resulttable tbody").empty();
    $("div.navigation").html(
        "<a href='" +
        "/api/users/" +
        "' onClick='followLink(event, this, renderUsers)'>Users</a>"+ " | " +
        "<a href ='" +
        "/api/bankaccounts/" +
        "' onClick='followLink(event, this, renderBankAccounts)'>Bank Accounts</a>"+ " | " +
        "<a href ='" +
        "/api/categories/" +
        "' onClick='followLink(event, this, renderCategories)'>Categories</a>")

    $(".resulttable thead").html(
        "<tr><th>Price</th><th>Date</th><th>Sender</th><th>Receiver</th><th>Category</th><th>Actions</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        tbody.append(transactionsRow(item));
    });
    renderTransactionForm(body["@controls"]["bumeta:add-transaction"]);
}

//renders the view for users collection
function renderUsers(body) {
    $("div.navigation").empty();
    $("div.deletebutton").empty();
    $("div.notification").empty();
    $("div.tablecontrols").empty();
    $(".resulttable tbody").empty();
    $("div.navigation").html(
        "<a href='" +
        "/api/transactions/" +
        "' onClick='followLink(event, this, renderTransactions)'>Transactions</a>"+ " | " +
        "<a href ='" +
        "/api/bankaccounts/" +
        "' onClick='followLink(event, this, renderBankAccounts)'>Bank Accounts</a>"+ " | " +
        "<a href ='" +
        "/api/categories/" +
        "' onClick='followLink(event, this, renderCategories)'>Categories</a>")
    $(".resulttable thead").html(
        "<tr><th>Username</th><th>Bankaccount</th><th>Actions</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        tbody.append(usersRow(item));
    });
    renderUserForm(body["@controls"]["bumeta:add-user"]);
}

//render the view for bank account collection
function renderBankAccounts(body) {
    $("div.navigation").empty();
    $("div.deletebutton").empty();
    $("div.notification").empty();
    $("div.tablecontrols").empty();
    $(".resulttable tbody").empty();
    $("div.navigation").html(
        "<a href='" +
        "/api/transactions/" +
        "' onClick='followLink(event, this, renderTransactions)'>Transactions</a>"+ " | " +
        "<a href ='" +
        "/api/users/" +
        "' onClick='followLink(event, this, renderUsers)'>Users</a>"+ " | " +
        "<a href ='" +
        "/api/categories/" +
        "' onClick='followLink(event, this, renderCategories)'>Categories</a>")
    $(".resulttable thead").html(
        "<tr><th>iban</th><th>Bank Name</th><th>User</th><th>Actions</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        tbody.append(bankAccountsRow(item));
    });
    renderBankAccountForm(body["@controls"]["bumeta:add-bank-account"]);
}

//renders the view for category collection
function renderCategories(body) {
    $("div.navigation").empty();
    $("div.deletebutton").empty();
    $("div.notification").empty();
    $("div.tablecontrols").empty();
    $(".resulttable tbody").empty();
    $("div.navigation").html(
        "<a href='" +
        "/api/transactions/" +
        "' onClick='followLink(event, this, renderTransactions)'>Transactions</a>"+ " | " +
        "<a href ='" +
        "/api/users/" +
        "' onClick='followLink(event, this, renderUsers)'>Users</a>"+ " | " +
        "<a href ='" +
        "/api/bankaccounts/" +
        "' onClick='followLink(event, this, renderBankAccounts)'>Bank Accounts</a>")
    $(".resulttable thead").html(
        "<tr><th>Name</th><th>transactions</th><th>Actions</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        tbody.append(categoriesRow(item));
    });
    renderCategoryForm(body["@controls"]["bumeta:add-category"]);
}

//start the client with connection to the API entry-point
function entrypoint(body) {

    getResource(body["@controls"]["bumeta:transactions-all"].href, renderTransactions)
}

//This ask for entrypoint connection.
$(document).ready(function () {
    getResource("http://localhost:5000/api/", entrypoint);
});
