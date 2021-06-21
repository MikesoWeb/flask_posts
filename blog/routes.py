from flask import render_template, flash, redirect, url_for, request
from blog import app, db, bcrypt

from blog.models import User
from flask_login import login_user, current_user, logout_user, login_required

from blog.forms import RegistrationForm, LoginForm, UpdateAccountForm


@app.route('/')
def home():
    count_user = User.query.count()
    list_user = User.query.all()
    return render_template('index.html', title='Main', count_user=count_user, list_user=list_user)


@app.route('/blog')
def blog():
    return render_template('blog.html', title='Blog')


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/contact')
def contact():
    return render_template('contact.html', title='Contacts')


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


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('You account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    user_all = [x.username for x in db.session.query(User.username).distinct()]
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form, user_all=user_all)


@app.route('/html_page')
def html_page():
    return render_template('html_page.html')


@app.route('/css_page')
def css_page():
    return render_template('css_page.html')


@app.route('/js_page')
def js_page():
    return render_template('js_page.html')


@app.route('/python_page')
def python_page():
    return render_template('python_page.html')


@app.route('/flask_page')
def flask_page():
    return render_template('flask_page.html')


@app.route('/django_page')
def django_page():
    return render_template('django_page.html')
