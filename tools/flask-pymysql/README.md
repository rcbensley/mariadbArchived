Flask-pymysql
================

Flask-pymysql is a fork of Flask-mysqldb, which instead uses the PyMySQL driver, which is a pure python driver.

Changelog
---------

### 0.2.3
This version now uses a kwarg dict which is passed to PyMySQL, there is no longer a curated list of attributes.
If you are migrating from Flask-mysqldb or and earlier version of Flask-pymysql, please see the example 'app.py',
or the Quickstart section below on how to make a dict for 'pymysql_kwargs'.

### 0.2.2
Fixing imports and references.

### 0.2.1
Fork of Flask-MySQLdb first change to PyMySQL.


Quickstart
----------

First, install Flask-pymysql:
    
    $ pip install flask-pymysql
    
Next, add a ``MySQL`` instance to your code.
The instance is configured using a dictionary of kwargs to pass to the PyMySQL connect class.
The key is named 'pymysql_kwargs'.
Please refer to the [PyMySQL documentation](https://pymysql.readthedocs.io/en/latest/modules/connections.html) for all options.

```python
from flask import Flask
from flask_pymysql import MySQL

app = Flask(__name__)

pymysql_connect_kwargs = {'user': 'BlackKnight',
                          'password': 'ILoveBridges',
                          'host': '127.0.0.1'}

app.config['pymysql_kwargs'] = pymysql_connect_kwargs
mysql = MySQL(app)

@app.route('/')
def users():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT user, host FROM mysql.user''')
    rv = cur.fetchall()
    return str(rv)

if __name__ == '__main__':
    app.run(debug=True)
```


Resources
---------

- [PyPI](https://pypi.python.org/pypi/Flask-pymysql)
- [PyMySQL](https://github.com/PyMySQL/PyMySQL)
