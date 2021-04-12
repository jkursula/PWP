# PWP SPRING 2021
# Perfectly Balanced: a budgeting tool
# Group information
* Student 1. Teemu Ikävalko teemu.ikavalko@student.oulu.fi
* Student 2. Essi Passoja essi.passoja@gmail.com
* Student 3. Tapio Kursula  tkursula@gmail.com


# Dependencies: (from requirements.txt file)
<ul>
<li>aniso8601==6.0.0</li>
<li>attrs==19.1.0</li>
<li>backcall==0.1.0</li>
<li>certifi==2019.3.9</li>
<li>chardet==3.0.4</li>
<li>Click==7.0</li>
<li>colorama==0.4.1</li>
<li>decorator==4.4.0</li>
<li>Flask==1.0.2</li>
<li>Flask-RESTful==0.3.7</li>
<li>Flask-SQLAlchemy==2.3.2</li>
<li>idna==2.8</li>
<li>ipython==7.4.0</li>
<li>ipython-genutils==0.2.0</li>
<li>itsdangerous==1.1.0</li>
<li>jedi==0.13.3</li>
<li>Jinja2==2.10</li>
<li>jsonschema==3.0.1</li>
<li>MarkupSafe==1.1.1</li>
<li>parso==0.3.4</li>
<li>pickleshare==0.7.5</li>
<li>prompt-toolkit==2.0.9</li>
<li>Pygments==2.3.1</li>
<li>pyrsistent==0.14.11</li>
<li>pytz==2018.9</li>
<li>requests==2.21.0</li>
<li>six==1.12.0</li>
<li>SQLAlchemy==1.3.1</li>
<li>traitlets==4.3.2</li>
<li>urllib3==1.24.1</li>
<li>wcwidth==0.1.7</li>
<li>Werkzeug==0.15.1</li>
<li>Python==3.8.5</li>
</ul>

# Note

If Python version of environment is 3.8 or higher, some modifications to the \_\_init\_\_.py file in flask_sqlalchemy folder need to be done.<br/>
On row 39 change:<br/>
_timer = time.perf_counter()  ==>  _timer = time.perf_counter

# Database

SQLite

# Instructions for running API 
install requirements from requirements.txt file and also: 
"flask", "flask-restful", "flask-sqlalchemy", "SQLAlchemy" using pip
set enviroment variables by issuing commands:

*set/export FLASK_APP=budgethub*

*set/export FLASK_ENV=development*

Initialize database by issuing command:

*flask init-db*

Populate database with sample data by issuing command:

*python populate_db.py*

run budgethub app using flask by inputting command:

*flask run*

# Instructions for testing

Same requirements as running the API but install also:
pytest, pytest-cov using pip.

run *pytest --cov-report term-missing --cov=budgethub*

This will run both database and API test simultaneously and also provide with covariance report with score of 97/100
