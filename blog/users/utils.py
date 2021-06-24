import os
import secrets

from PIL import Image
from flask import url_for, current_app
from flask_login import current_user
from flask_mail import Message

from blog import mail



def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    full_path = os.path.join(current_app.root_path, 'static', 'profile_pics/', current_user.username)
    if not os.path.exists(full_path):
        os.mkdir(full_path)
    picture_path = os.path.join(full_path, picture_fn)
    output_size = (350, 350)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f"""
    Чтобы сбросить ваш пароль, перейдите по этой ссылке:
    {url_for('users.reset_token', token=token, _external=True)}

    Если вы не делали данный запрос, просто проигнорируйте это письмо!
    Никаких изменений произведено не будет!
    """
    mail.send(msg)