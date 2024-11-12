import dj_database_url
from .common import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = []

USE_SERVER_DB = False


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES = {
    'default': (
        dj_database_url.parse(environ.get('RENDER_DATABASE_URL')) 
        if USE_SERVER_DB else {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': environ.get('PG_DATABASE_NAME'),
            'USER': environ.get('PG_DATABASE_USER'),
            'PASSWORD': environ.get('PG_DATABASE_PASSWORD'),
            # 'HOST': 'localhost', # environ.get('PG_DATABASE_HOST'),
            # 'PORT': '5432' # environ.get('PG_DATABASE_PORT'),
        }
    )

    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }
}