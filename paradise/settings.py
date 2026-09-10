# D:\Paradise\paradise\settings.py
import os
import sys
import dj_database_url
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-key')
DEBUG = False
ALLOWED_HOSTS = ['*', '.vercel.app', ' https://online-vape-shop-paradise.vercel.app']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'catalog',      # ✅ Название приложения
    'django_filters',
    'dashboard',
    'cart',
    'storages',
]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'paradise.urls'
WSGI_APPLICATION = 'paradise.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart',
                'catalog.context_processors.categories',
            ],
        },
    },
]

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'



STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "access_key": os.getenv('B2_APPLICATION_KEY_ID'),
            "secret_key": os.getenv('B2_APPLICATION_KEY'),
            "bucket_name": os.getenv('B2_BUCKET_NAME'),
            "region_name": os.getenv('B2_REGION'),
            "endpoint_url": f"https://s3.{os.getenv('B2_REGION')}.backblazeb2.com",
            "file_overwrite": False,
            # "default_acl": "public-read",  # НЕ НУЖНО для приватного бакета
            "querystring_auth": True,  # Включает pre-signed URLs
            "querystring_expire": 3600,  # Время жизни ссылки (1 час)
        },
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# URL для доступа к медиафайлам (будет генерировать pre-signed URL)
MEDIA_URL = f"https://{os.getenv('B2_BUCKET_NAME')}.s3.{os.getenv('B2_REGION')}.backblazeb2.com/"
# AWS_ACCESS_KEY_ID = os.getenv('BLOB_READ_WRITE_TOKEN')

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'