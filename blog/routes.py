import secrets, os, shutil
from PIL import Image
from flask import render_template, flash, redirect, url_for, request, abort

from blog import app, db, bcrypt

from blog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

from blog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm


@app.route('/')
def home():
    return render_template('index.html', title='Главная')


@app.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=2)
    return render_template('blog.html', title='Блог>', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html', title='О блоге')


@app.route('/contact')
def contact():
    return render_template('contact.html', title='Контакты')


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

        full_path = os.path.join(app.root_path, 'static', 'profile_pics', user.username)
        if not os.path.exists(full_path):
            os.mkdir(full_path)
        shutil.copy(f'{app.root_path}/static/profile_pics/default.jpg', full_path)
        flash('Ваш аккаунт был создан. Вы можете войти на блог', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, title='Регистрация')


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
            flash('Войти не удалось. Пожалуйста, проверьте электронную почту или пароль', 'danger')
    return render_template('login.html', form=form, title='Логин')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    full_path = os.path.join(app.root_path, 'static', 'profile_pics/', current_user.username)
    if not os.path.exists(full_path):
        os.mkdir(full_path)
    picture_path = os.path.join(full_path, picture_fn)
    output_size = (350, 350)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Ваш аккаунт был обновлён!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename=f'profile_pics/' + current_user.username + '/' + current_user.image_file)
    user_all = [x.username for x in db.session.query(User.username).distinct()]
    return render_template('account.html', title='Аккаунт',
                           image_file=image_file, form=form, user_all=user_all)


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Данный пост был обновлён!', 'success')
        return redirect(url_for('blog'))
    return render_template('create_post.html', title='Новая статья',
                           form=form, legend='Новая статья')


@app.route('/post/<int:post_id>')
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Данный пост был обновлён', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':

        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Обновить статью',
                           form=form, legend='Обновить статью')


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Данный пост был удален', 'success')
    return redirect(url_for('blog'))


@app.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc()) \
        .paginate(page=page, per_page=3)
    return render_template('user_posts.html', title='Блог>', posts=posts, user=user)


@app.route('/html_page')
@login_required
def html_page():
    return render_template('html_page.html')


@app.route('/css_page')
@login_required
def css_page():
    return render_template('css_page.html')


@app.route('/js_page')
@login_required
def js_page():
    return render_template('js_page.html')


@app.route('/python_page')
@login_required
def python_page():
    return render_template('python_page.html')


@app.route('/flask_page')
@login_required
def flask_page():
    return render_template('flask_page.html')


@app.route('/django_page')
@login_required
def django_page():
    return render_template('django_page.html')
