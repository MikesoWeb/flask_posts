from flask import render_template, request, Blueprint
from flask_login import login_required

from blog.models import Post

main = Blueprint('main', __name__)


@main.route('/')
def home():
    return render_template('index.html', title='Главная')


@main.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()) \
        .paginate(page=page, per_page=2)
    return render_template('blog.html', title='Блог>', posts=posts)


@main.route('/about')
def about():
    return render_template('about.html', title='О блоге')


@main.route('/contact')
def contact():
    return render_template('contact.html', title='Контакты')


@main.route('/html_page')
@login_required
def html_page():
    return render_template('html_page.html')


@main.route('/css_page')
@login_required
def css_page():
    return render_template('css_page.html')


@main.route('/js_page')
@login_required
def js_page():
    return render_template('js_page.html')


@main.route('/python_page')
@login_required
def python_page():
    return render_template('python_page.html')


@main.route('/flask_page')
@login_required
def flask_page():
    return render_template('flask_page.html')


@main.route('/django_page')
@login_required
def django_page():
    return render_template('django_page.html')
