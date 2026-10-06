from flask import Flask
from flask_pymysql import MySQL

app = Flask(__name__)

# This example assumes a valid username and password are in the client section of a ~/.my.cnf file.
# This is a well known standard for mysql/mariadb clients.
# Example contents of ~/.my.cnf :
# [client]
# user = my_user_name
# password = super_secret_password
# This means your password is now not stored with your code!

connect_args = {'read_default_file': '~/.my.cnf',
                'autocommit': True,
                'cursorclass': 'DictCursor'}

app.config['pymysql_kwargs'] = connect_args

mysql = MySQL(app)


@app.route('/')
def users():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT user, host FROM mysql.user''')
    rv = cur.fetchall()
    return str(rv)


if __name__ == '__main__':
    app.run(debug=True)
