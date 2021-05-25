from flask import Flask, render_template
from articles import posts

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', title='Main page')


@app.route('/blog')
def blog():
    return render_template('blog.html', title='Blog page', posts=posts)


if __name__ == '__main__':
    app.run(debug=True)
