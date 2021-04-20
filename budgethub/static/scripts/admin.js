"use strict"; 
const DEBUG = true;
const MASONJSON = "application/vnd.mason+json";
const PLAINJSON = "application/json";

function renderError(jqxhr) {
    let msg = jqxhr.responseJSON["@error"]["@message"];
    $("div.notification").html("<p class='error'>" + msg + "</p>");
}

function renderMsg(msg) {
    $("div.notification").html("<p class='msg'>" + msg + "</p>");
}

function getResource(href, renderer) {
    $.ajax({
        url: href,
        success: renderer,
        error: renderError
    });
}

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

function deleteData(href, postProcessor) {
$.ajax({
    url: href,
    type: "DELETE",
    success: postProcessor,
    error: renderError
});
}

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

function usersRow(item) {
    let link = "<a href='" +
                item["@controls"].self.href +
                "' onClick='followLink(event, this, renderUser)'>Edit</a>";

    return "<tr><td>" + item.username +
            "</td><td>" + item.bankAccount + 
            "</td><td>" + link + "</td></tr>";
}

function bankAccountsRow(item) {
    let link = "<a href='" +
                item["@controls"].self.href +
                "' onClick='followLink(event, this, renderBankAccount)'>Edit</a>";

    return "<tr><td>" + item.iban +
            "</td><td>" + item.bankName +
            "</td><td>" + item.user + 
            "</td><td>" + link + "</td></tr>";
}

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

function userRow(item) {

    return "<tr><td>" + item.username +
            "</td><td>" + item.bankAccount + "</td></tr>";
}

function bankAccountRow(item) {

    return "<tr><td>" + item.iban +
            "</td><td>" + item.bankName + "</td></tr>";
}

function categoryRow(item) {

    return "<tr><td>" + item.category_name + "</td></tr>";
}

//Not needed no pagination
function appendTransactionRow(body) {
    $(".resulttable tbody").append(transactionRow(body));
}

function appendUserRow(body) {
    $(".resulttable tbody").append(userRow(body));
}

function appendBankAccountRow(body) {
    $(".resulttable tbody").append(bankAccountRow(body));
}

function appendCategoryRow(body) {
    $(".resulttable tbody").append(categoryRow(body));
}
//Might be needed
function getSubmittedTransaction(data, status, jqxhr) {
    renderMsg("Successful");
    let href = jqxhr.getResponseHeader("Location");
    if (href) {
        getResource(href, appendTransactionRow);
    }
}

function getSubmittedUser(data, status, jqxhr) {
    renderMsg("Successful");
    let href = jqxhr.getResponseHeader("Location");
    if (href) {
        getResource(href, appendUserRow);
    }
}

function getSubmittedBankAccount(data, status, jqxhr) {
    renderMsg("Successful");
    let href = jqxhr.getResponseHeader("Location");
    if (href) {
        getResource(href, appendBankAccountRow);
    }
}

function getSubmittedCategory(data, status, jqxhr) {
    renderMsg("Successful");
    let href = jqxhr.getResponseHeader("Location");
    if (href) {
        getResource(href, appendCategoryRow);
    }
}

function followLink(event, a, renderer) {
    event.preventDefault();
    getResource($(a).attr("href"), renderer);
}


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

function submitUser(event) {
    event.preventDefault();

    let data = {};
    let form = $("div.form form");
    data.username = $("input[name='username']").val();
    data.password = $("input[name='password']").val();
    data.bankAccount = $("input[name='bankAccount']").val().split(",");
    sendData(form.attr("action"), form.attr("method"), data, getSubmittedUser);
}

function submitBankAccount(event) {
    event.preventDefault();

    let data = {};
    let form = $("div.form form");
    data.iban = $("input[name='iban']").val();
    data.bankName = $("input[name='bankName']").val();
    sendData(form.attr("action"), form.attr("method"), data, getSubmittedBankAccount);
}

function submitCategory(event) {
    event.preventDefault();

    let data = {};
    let form = $("div.form form");
    data.category_name = $("input[name='category_name']").val();
    sendData(form.attr("action"), form.attr("method"), data, getSubmittedCategory);
}

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

//modify this
function renderTransaction(body) {
    $("div.navigation").html(
        "<a href='" +
        body["@controls"]["bumeta:transactions-all"].href +
        "' onClick='followLink(event, this, renderTransactions)'>Transaction Collection</a>" + " | " +
        "<a href='" +
        body["@controls"]["bumeta:transactions-all"].href +
        "' onClick=' deleteData(/api/transactions/1/))'>Delete</a>"
    );
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    //renderTransactionForm(body["@controls"].self);
    $("input[name='price']").val(body.price);
    $("input[name='dateTime']").val(body.dateTime);
    $("input[name='sender']").val(body.sender);
    $("input[name='receiver']").val(body.receiver);
    $("input[name='category']").val(body.category);
    /*$("form input[type='submit']").before(
        "<label>Location</label>" +
        "<input type='text' name='location' value='" +
        body.location + "' readonly>"
    );*/
    $("div.deletebutton").html('<button class="btn_delete">DELETE</button>');
    $("div.deletebutton").click(deleteData(body["@controls"]["bumeta:delete"].href));
}

function renderUser(body) {
    $("div.navigation").html(
        "<a href='" +
        body["@controls"]["bumeta:users-all"].href +
        "' onClick='followLink(event, this, renderUsers)'>Users Collection</a>" + " | " +
        "<a href='" +
        body["@controls"]["bumeta:users-all"].href +
        "' onClick=' deleteData(/api/transactions/1/))'>Delete</a>"
    );
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    renderUserForm(body["@controls"].edit);
    $("input[name='username']").val(body.username);
    $("input[name='bankAccount']").val(body.bankAccount);
    $("form input[type='submit']").before(
        "<label>Location</label>" +
        "<input type='text' name='location' value='" +
        body.location + "' readonly>"
    );
    $("div.deletebutton").html('<button class="btn_delete">DELETE</button>');
    $("div.deletebutton").click(deleteData(body["@controls"]["bumeta:delete"].href));
}

function renderBankAccount(body) {
    $("div.navigation").html(
        "<a href='" +
        body["@controls"]["bumeta:banks-all"].href +
        "' onClick='followLink(event, this, renderBankAccounts)'>Bank Account Collection</a>" + " | " +
        "<a href='" +
        body["@controls"]["self"].href +
        "' onClick=' deleteData(/api/transactions/1/))'>Delete</a>"
    );
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    renderBankAccountForm(body["@controls"].edit);
    $("input[name='iban']").val(body.iban);
    $("input[name='bankName']").val(body.bankName);
    $("input[name='user']").val(body.user);
    $("form input[type='submit']").before(
        "<label>Location</label>" +
        "<input type='text' name='location' value='" +
        body.location + "' readonly>"
    );
    $("div.deletebutton").html('<button class="btn_delete">DELETE</button>');
    $("div.deletebutton").click(deleteData(body["@controls"]["bumeta:delete"].href));
}

function renderCategory(body) {
    $("div.navigation").html(
        "<a href='" +
        body["@controls"]["bumeta:categories-all"].href +
        "' onClick='followLink(event, this, renderCategories)'>Category Collection</a>" + " | " +
        "<a href='" +
        body["@controls"]["self"].href +
        "' onClick=' deleteData(/api/transactions/1/))'>Delete</a>"
    );
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    renderCategoryForm(body["@controls"].edit);
    $("input[name='category_name']").val(body.category_name);
    $("form input[type='submit']").before(
        "<label>Location</label>" +
        "<input type='text' name='location' value='" +
        body.location + "' readonly>"
    );
    $("div.deletebutton").html('<button class="btn_delete">DELETE</button>');
    $("div.deletebutton").click(deleteData(body["@controls"]["bumeta:delete"].href));
}
function renderTransactions(body) {
    $("div.navigation").empty()
    
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

    $("div.tablecontrols").empty();
    $(".resulttable tbody").empty();
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

function renderUsers(body) {
    $("div.navigation").empty()
    
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

    $("div.tablecontrols").empty();
    $(".resulttable tbody").empty();
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

function renderBankAccounts(body) {
    $("div.navigation").empty()
    
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

    $("div.tablecontrols").empty();
    $(".resulttable tbody").empty();
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

function renderCategories(body) {
    $("div.navigation").empty()
    
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

    $("div.tablecontrols").empty();
    $(".resulttable tbody").empty();
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

$(document).ready(function () {
    getResource("http://localhost:5000/api/transactions/", renderTransactions);
});
