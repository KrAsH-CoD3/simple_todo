from .common import *


SECRET_KEY = environ.get('TODO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    'simple-todo-5824.onrender.com',
    '127.0.0.1:3000',
]

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
import dj_database_url

DATABASES = {
    'default': dj_database_url.parse(environ.get('DATABASE_URL'))
}