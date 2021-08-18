from flask import render_template, request, Blueprint, url_for
from flask_login import login_required, current_user

from blog.models import Post

main = Blueprint('main', __name__, template_folder='templates')


@main.route('/')
def home():
    return render_template('main/index.html', title='Главная')


@main.route('/blog', methods=['POST', 'GET'])
def blog():
    post = Post.query.get_or_404(current_user.id)
    if post:
        page = request.args.get('page', 1, type=int)
        posts = Post.query.order_by(Post.date_posted.desc()) \
            .paginate(page=page, per_page=2)
        image_file = url_for('static',
                             filename=f'profile_pics/{current_user.username}/{post.image_post}')

        return render_template('main/blog.html', title='Блог>', posts=posts, image_file=image_file)


@main.route('/about')
def about():
    return render_template('main/about.html', title='О блоге')


@main.route('/contact')
def contact():
    return render_template('main/contact.html', title='Контакты')


@main.route('/html_page')
@login_required
def html_page():
    return render_template('main/html_page.html')


@main.route('/css_page')
@login_required
def css_page():
    return render_template('main/css_page.html')


@main.route('/js_page')
@login_required
def js_page():
    return render_template('main/js_page.html')


@main.route('/python_page')
@login_required
def python_page():
    return render_template('main/python_page.html')


@main.route('/flask_page')
@login_required
def flask_page():
    return render_template('main/flask_page.html')


@main.route('/django_page')
@login_required
def django_page():
    return render_template('main/django_page.html')
