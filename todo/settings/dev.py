from .common import *


SECRET_KEY = environ.get('TODO_SECRET_KEY')
ALLOWED_HOSTS = []
DEBUG = True


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# DATABASES = {
#     # 'default': dj_database_url.parse(environ.get('DATABASE_URL')),
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': environ.get('PG_DATABASE_NAME'),
#         'USER': environ.get('PG_DATABASE_USER'),
#         'PASSWORD': environ.get('PG_DATABASE_PASSWORD'),
#         'HOST': environ.get('PG_DATABASE_HOST'),
#         'PORT': environ.get('PG_DATABASE_PORT'),
#     }
# }