from flask import render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
from hashlib import sha256
from werkzeug import security
from app001 import app
from datetime import datetime
# from flask_wtf.csrf import  CSRFProtect

app.secret_key = 'woguddld'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'choi'
app.config['MYSQL_PASSWORD'] = 'wogud'
app.config['MYSQL_DB'] = 'login_test'
app.config['MYSQL_PORT'] = 3306

# Intialize MySQL
mysql = MySQL(app)

# ''' CSRF Init '''
# csrf = CSRFProtect()
# csrf.init_app(app)

class User:
    @staticmethod
    def check_username_exist(username):
        # Implement the logic to check if the username already exists in the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        return cursor.fetchone() is not None

    @staticmethod
    def check_email_exist(email):
        # Implement the logic to check if the email already exists in the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
        return cursor.fetchone() is not None

    @staticmethod
    def useradd(username, password, email):
        # Implement the logic to add a new user to the database
        hashed_password = hash_password(password)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO accounts (username, password, email) VALUES (%s, %s, %s)', (username, hashed_password, email))
        mysql.connection.commit()

def hash_password(password):
    return sha256(password.encode()).hexdigest()

@app.route('/login/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # 쉬운 checking을 위해 변수에 값 넣기
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account and account['password'] == hash_password(password):
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('home'))
        else:
            msg = '아이디 또는 비밀번호가 일치하지 않습니다.'
    return render_template('login.html', msg=msg)


@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/board', methods=['GET', 'POST'])
def board():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        message = request.form['message']
        timestamp = datetime.now()
        username = session['username']

        if message:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO forum_messages (username, message, timestamp) VALUES (%s, %s, %s)',
                           (username, message, timestamp))
            mysql.connection.commit()
            flash('메시지가 성공적으로 게시되었습니다!', 'success')
        else:
            flash('메시지는 비워둘 수 없습니다!', 'error')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM forum_messages ORDER BY timestamp DESC')
    posts = cursor.fetchall()

    for post in posts:
        if post['username'] == session['username']:
            post['edit'] = True
        else:
            post['edit'] = False

    return render_template('board.html', posts=posts)

@app.route('/edit_message/<int:message_id>', methods=['GET', 'POST'])
def edit_message(message_id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM forum_messages WHERE id = %s', [message_id])
    post = cursor.fetchone()

    if request.method == 'POST':
        new_message = request.form['new_message']
        if new_message:
            cursor.execute('UPDATE forum_messages SET message = %s WHERE id = %s', (new_message, message_id))
            mysql.connection.commit()
            flash('메시지가 성공적으로 수정되었습니다!', 'success')
        else:
            flash('새 메시지는 비워둘 수 없습니다!', 'error')
        return redirect(url_for('board'))

    return render_template('edit_message.html', post=post)


@app.route('/delete_message/<int:message_id>', methods=['POST'])
def delete_message(message_id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM forum_messages WHERE id = %s', [message_id])
    mysql.connection.commit()
    flash('메시지가 성공적으로 삭제되었습니다!', 'success')

    return redirect(url_for('board'))

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = '회원가입 페이지'
    # If already loggedin, redirect to home
    if 'loggedin' in session:
        return redirect(url_for('home'))
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        username_already_exist = User.check_username_exist(username)
        email_already_exist = User.check_email_exist(email)
        if username_already_exist:
            msg = 'That username is already exist'
        elif email_already_exist:
            msg = 'That email is already exist'
        else:
            User.useradd(username, password, email)
            msg = 'Create User Success!'
            return redirect(url_for('login'))
    return render_template('register.html', msg=msg)