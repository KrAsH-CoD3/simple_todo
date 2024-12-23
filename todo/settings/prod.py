import dj_database_url
from .common import *


DEBUG = False

ALLOWED_HOSTS = [
    'simple-todo-5824.onrender.com',
    *environ.get('ALLOWED_HOSTS').split(',')
]

DATABASES = {
    'default': dj_database_url.parse(environ.get('RENDER_DATABASE_URL'))
}