from flask import Flask, render_template, flash, redirect, url_for
from articles import posts
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '90cca34fc5f74076b4f6081061726727'


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
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('blog'))
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


if __name__ == '__main__':
    app.run(debug=True)
