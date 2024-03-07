from flask import render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from app001 import app
from datetime import datetime

app.secret_key = 'woguddld'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'choi'
app.config['MYSQL_PASSWORD'] = 'wogud'
app.config['MYSQL_DB'] = 'login_test'
app.config['MYSQL_PORT'] = 3306

# Intialize MySQL
mysql = MySQL(app)


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
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO accounts (username, password, email) VALUES (%s, %s, %s)', (username, password, email))
        mysql.connection.commit()


@app.route('/login/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    # username과 password에 입력값이 있을 경우
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # 쉬운 checking을 위해 변수에 값 넣기
        username = request.form['username']
        password = request.form['password']
        # MySQL DB에 해당 계정 정보가 있는지 확인
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        # 값이 유무 확인 결과값 account 변수로 넣기
        account = cursor.fetchone()
        # 정상적으로 유저가 있으면 새로운 세션 만들고, 없으면 로그인 실패 문구 출력하며 index 리다이렉트
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)


@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# # Flask 파이썬 코드
# @app.route('/home', methods=['GET', 'POST'])
# def home():
#     error = None

#     if 'loggedin' not in session:
#         return redirect(url_for('login'))

#     if request.method == 'POST':
#         content = request.form['content']
#         conn = mysql.connect()
#         cursor = conn.cursor(dictionary=True)

#         try:
#             # 'content' 테이블에 'times' 컬럼이 있다고 가정합니다.
#             sql = "INSERT INTO content (id, content, times) VALUES (%s, %s, %s)"
#             cursor.execute(sql, (session['id'], content, datetime.now()))
#             conn.commit()
#             cursor.close()
#         except Exception as e:
#             error = f"콘텐츠 추가 중 오류 발생: {e}"

#         return redirect(url_for("home"))

#     elif request.method == 'GET':
#         conn = mysql.connect()
#         cursor = conn.cursor(dictionary=True)
#         sql = "SELECT content, id, times FROM content ORDER BY times desc"
#         cursor.execute(sql)
#         data = cursor.fetchall()

#         data_list = []

#         for obj in data:
#             data_dic = {
#                 'con': obj['content'],
#                 'writer': obj['id'],
#                 'time': obj['times']
#             }
#             data_list.append(data_dic)

#         cursor.close()
#         conn.close()

#         return render_template('home.html', error=error, name=session['username'], data_list=data_list)

#     return render_template('home.html', error=error, name=session['username'])



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
    msg = 'Creating User Page'
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