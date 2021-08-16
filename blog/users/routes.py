import os
import shutil
from datetime import datetime

from flask import Blueprint, request, render_template, url_for, flash, g
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.utils import redirect

from blog import bcrypt, db
from blog.models import User, Post
from blog.users.forms import RequestResetForm, ResetPasswordForm, UpdateAccountForm, RegistrationForm, LoginForm
from blog.users.utils import send_reset_email, save_picture

users = Blueprint('users', __name__)


@users.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        old_img = g.user.image_file
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.blog'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        full_path = os.path.join(os.getcwd(), 'blog/static', 'profile_pics', user.username)
        if not os.path.exists(full_path):
            os.mkdir(full_path)
        shutil.copy(f'{os.getcwd()}/blog/static/profile_pics/default.jpg', full_path)
        flash('Ваш аккаунт был создан. Вы можете войти на блог', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', form=form, title='Регистрация', legend='Регистрация')


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
    return render_template('login.html', form=form, title='Логин', legend='Войти')


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    old_img = url_for('static',
                      filename=f'profile_pics/{g.user}/default.jpg')
    form = UpdateAccountForm()
    if request.method == 'GET':
        form.username.data = g.user.username
        form.email.data = g.user.email
    elif form.validate_on_submit():
        g.user.username = form.username.data
        g.user.email = form.email.data
        if form.picture.data:
            g.user = save_picture(form.picture.data)
        else:
            form.picture.data = g.user.image_file

        db.session.commit()
        flash('Ваш аккаунт был обновлён!', 'success')
        return redirect(url_for('users.account'))
    image_file = url_for('static', filename=f'profile_pics/' + g.user.username + '/' + g.user.image_file)
    user_all = [x.username for x in db.session.query(User.username).distinct()]
    return render_template('account.html', title='Аккаунт',
                           image_file=image_file, form=form, user_all=user_all)


@users.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user) \
        .order_by(Post.date_posted.desc()) \
        .paginate(page=page, per_page=3)
    return render_template('user_posts.html', title='Блог>', posts=posts, user=user)


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
    return render_template('reset_request.html', form=form, title='Сброс пароля')


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
    return render_template('reset_token.html', form=form, title='Сброс пароля')
