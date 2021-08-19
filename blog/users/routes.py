import base64
import os
from datetime import datetime

from flask import Blueprint, request, render_template, url_for, flash, g
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.utils import redirect

from blog import bcrypt, db
from blog.models import User, Post
from blog.users.forms import RequestResetForm, ResetPasswordForm, UpdateAccountForm, RegistrationForm, LoginForm
from blog.users.utils import send_reset_email

users = Blueprint('users', __name__, template_folder='templates')


@users.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


@users.route('/register', methods=['GET', 'POST'])
def register():
    # if current_user.is_authenticated:
    #     return redirect(url_for('main.blog'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        if form.picture.data:
            user.picture = form.picture.data
            user.picture.read()
            db.session.commit()
        else:
            print(10 * 'None')
        flash('Ваш аккаунт был создан. Вы можете войти на блог', 'success')
        return redirect(url_for('users.login'))
    context = {
        'form': form,
        'title': 'Регистрация',
        'legend': 'Регистрация'
    }
    return render_template('users/register.html', **context)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.blog'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('users.account'))
        else:
            flash('Войти не удалось. Пожалуйста, проверьте электронную почту или пароль', 'danger')
    return render_template('users/login.html', form=form, title='Логин', legend='Войти')


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    # текущий пользователь User(Леван, levan@microsoft.com, 20e8c05326b36d6f.png)
    user = User.query.filter_by(username=current_user.username).first()
    posts = Post.query.all()
    users = User.query.all()
    form = UpdateAccountForm()
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.picture.data:
            # current_user.picture = save_picture(form.picture.data)
            current_user.picture = form.picture.data.read()
            print(current_user.picture, '##############)')
            # db.session.add(current_user.picture)
            db.session.commit()
            flash('Ваш аккаунт был обновлён!', 'success')
            return redirect(url_for('users.account'))

        else:
            print(20 * '#')
    img_file = base64.b64encode(current_user.picture).decode(
        'ascii') if current_user.picture else ''

    # image_file = url_for('static', filename=f'profile_pics/' + current_user.username + '/' + current_user.image_file)
    return render_template('users/account.html', title='Аккаунт',
                           form=form, posts=posts, users=users, user=user, img_file=img_file)


@users.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user) \
        .order_by(Post.date_posted.desc()) \
        .paginate(page=page, per_page=3)
    author_picture = user.picture

    img_file = base64.b64encode(author_picture).decode('ascii') if author_picture else ''

    return render_template('users/user_posts.html', title='Блог>', posts=posts, user=user, img_file=img_file)


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.blog'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('На указанный емайл были отправлены инструкции по восстановлению пароля', 'info')
        return redirect(url_for('users.login'))
    return render_template('users/reset_request.html', form=form, title='Сброс пароля')


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.blog'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Ваш пароль был обновлён! Вы можете войти на блог', 'success')
        return redirect(url_for('users.login'))
    return render_template('users/reset_token.html', form=form, title='Сброс пароля')


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))
