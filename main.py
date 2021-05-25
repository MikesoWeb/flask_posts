from flask import Flask, render_template
from articles import posts

app = Flask(__name__)


@app.route('/')
def index():
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


if __name__ == '__main__':
    app.run(debug=True)
