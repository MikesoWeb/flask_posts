from flask import render_template, flash, redirect, url_for
from blog import app, db, bcrypt

from blog.articles import posts
from blog.models import User

from forms import RegistrationForm, LoginForm


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
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('blog'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form, title='Login')
