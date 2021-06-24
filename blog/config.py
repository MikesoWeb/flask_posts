import os


class Config:
    """SECRET_KEY и SQLALCHEMY_DATABASE_URI добавим в os.environ.get()
        SECRET_KEY = os.environ.get('SECRET_KEY')
        SECRET_KEY = os.environ.get('SQLALCHEMY_DATABASE_URI')
        с помощью  set или bat
        MAIL_USERNAME и MAIL_PASSWORD тоже самое
    """
    SECRET_KEY = '90cca34fc5f74076b4f6081061726727'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
