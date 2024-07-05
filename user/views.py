from flask import (
    Blueprint, request, abort, render_template, redirect, url_for, flash
)
from http import HTTPStatus
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user, logout_user

from app import db
from .models import User

user_bp = Blueprint('user', __name__, url_prefix='user')


@user_bp.route('/register', methods=('GET', 'POST'))
def register():
    """用户注册"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        re_password = request.form['re_password']
        email = request.form['email']
        nickname = request.form['nickname']
        if password != re_password:
            abort(HTTPStatus.BAD_REQUEST)
        hash_password = generate_password_hash(password)
        user = User(username=username, password=hash_password, email=email, nickname=nickname)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user.login'))

    return render_template('user/register.html')


@user_bp.route('/login', methods=('GET', 'POST'))
def login():
    """用户登录"""
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.session.execute(
            db.select(User).filter(User.username == username)
        ).scalar()
        if user is None or not check_password_hash(user.password, password):
            error = '用户名或密码错误'
        else:
            login_user(user)
            return redirect('/')

    if error is not None:
        flash(error, 'danger')
    return render_template('user/login.html')


@user_bp.route('/logout', methods=('GET', 'POST'))
@login_required
def logout():
    logout_user()
    return redirect(url_for('user.login'))


@user_bp.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html')
