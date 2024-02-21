from flask import Flask, Blueprint, request, render_template, make_response, jsonify, redirect, url_for
from flask_login import login_user, current_user
from blog_control.user_mgmt import User

blog_abtest = Blueprint('blog',__name__)

@blog_abtest.route('/set_email', methods=['GET','POST'])
def set_email():
    if request.method == 'GET':
        print('set_email', request.args.get('user_email'))
        return redirect(url_for('blog.test_blog'))
    else:
        # print('set_email',request.headers)
        # content type 이 application/json 인 경우
        # print('set_email',request.get_json())
        print('set_email',request.form['user_email'])
        user = User.create(request.form['user_email'], 'A')
        login_user(user)

        return redirect(url_for('blog.test_blog'))
    
    # print(request.args.get('user_email'))
    # return redirect(url_for('blog.test_blog'))
    # return redirect('/blog/test_blog')
    # return make_response(jsonify(success=True), 200)


@blog_abtest.route('/test_blog')
def test_blog():
    if current_user.is_authenticated:
        return render_template('blog_A.html', user_email = current_user.user_email)
    else:
        return render_template('blog_A.html')