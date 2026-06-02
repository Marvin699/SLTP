"""
Django settings for the Smart Low-Altitude Emergency Transportation Teaching Platform.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-smart-low-altitude-emergency-transport-2024'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Path Planning Agent - FastAPI backend configuration
PATH_PLANNING_DB_PATH = os.environ.get(
    'PATH_PLANNING_DB_PATH',
    str(BASE_DIR / 'path_planning_data.db')
)

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True
