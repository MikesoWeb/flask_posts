from flask import render_template, flash, redirect, url_for, request
from blog import app, db, bcrypt

from blog.articles import posts
from blog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

from blog.forms import RegistrationForm, LoginForm


@app.route('/')
def home():
    return render_template('index.html', title='Main')


@app.route('/blog')
def blog():
    return render_template('blog.html', title='Blog', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html', title='About', posts=posts)


@app.route('/contact')
def contact():
    return render_template('contact.html', title='Contacts', posts=posts)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('blog'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('You account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, title='Register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('blog'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('account'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form, title='Login')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/account')
@login_required
def account():
    return render_template('account.html', title='Account')
