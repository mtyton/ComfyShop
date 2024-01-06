"""
Django settings for arwagtail_storetel project.

Generated by 'django-admin startproject' using Django 4.1.8.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# -> GlitchTip error reporting 
sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN", ''),
    integrations=[DjangoIntegration()],
    auto_session_tracking=False,
    traces_sample_rate=0
) 

SENTRY_ENVIRONMENT = os.environ.get("SENTRY_ENVIRONMENT", '')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/


# Application definition

INSTALLED_APPS = [
    "home",
    "store",
    "mailings",
    "blog",
    "search",
    "dynamic_forms",
    "setup",
    "wagtail_localize",
    "wagtail_localize.locales",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.simple_translation",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    'wagtail.contrib.modeladmin',
    "wagtail.contrib.settings",
    "wagtail",
    "wagtailmenus",
    "modelcluster",
    "taggit",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "phonenumber_field",
    "django_celery_results",
    "django_celery_beat",
    "easy_thumbnails"
]


MIDDLEWARE = [
    "setup.middleware.CheckSetupMiddleware",
    "setup.middleware.CheckShopMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    'django.middleware.locale.LocaleMiddleware',
    "wagtail.contrib.redirects.middleware.RedirectMiddleware"
]

ROOT_URLCONF = "wagtail_store.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(PROJECT_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                'setup.context_processors.config_context_processor',
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                'django.template.context_processors.i18n',
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                'wagtailmenus.context_processors.wagtailmenus',
            ],
        },
    },
]

WSGI_APPLICATION = "wagtail_store.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
import dj_database_url as db_url

DATABASES = {
    "default": db_url.parse(
        os.environ.get("DATABASE_URL", "postgres://comfy:password@db/comfy_shop")
    )
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

WAGTAIL_I18N_ENABLED = True

WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    ('en', "English"),
    ('pl', "Polish"),
 ]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, "static"),
]

# ManifestStaticFilesStorage is recommended in production, to prevent outdated
# JavaScript / CSS assets being served from cache (e.g. after a Wagtail upgrade).
# See https://docs.djangoproject.com/en/4.1/ref/contrib/staticfiles/#manifeststaticfilesstorage
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"


# Wagtail settings

WAGTAIL_SITE_NAME = "wagtail_store"

# Search
# https://docs.wagtail.org/en/stable/topics/search/backends.html
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
WAGTAILADMIN_BASE_URL = "https://wagtail_store.tepewu.pl"

# Messages
from django.contrib import messages

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"
MESSAGE_TAGS = {
    messages.DEBUG: "debug",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}


# STORE SETTINGS
PRODUCTS_PER_PAGE = 6

# CART settings
CART_SESSION_ID = 'cart'

# EMAIL settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", '')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'wagtail_store-sklep@tepewu.pl')

# CELERY settings
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")
CELERY_CACHE_BACKEND = os.environ.get("CELERY_CACHE_BACKEND")
CELERY_TIMEZONE = os.environ.get("CELERY_TIMEZONE")
CELERY_TASK_TRACK_STARTED = os.environ.get("CELERY_TASK_TRACK_STARTED")
CELERY_TASK_TIME_LIMIT = os.environ.get("CELERY_TASK_TIME_LIMIT")
# CELERY_RESULT_BACKEND_DB = f'db+mysql+pymysql://{os.environ.get("MYSQL_USER")}:{os.environ.get("MYSQL_PASSWORD")}@db/{os.environ.get("MYSQL_DATABASE")}'
CELERY_BROKER_URL = f'amqp://{os.environ.get("RABBITMQ_DEFAULT_USER")}:{os.environ.get("RABBITMQ_DEFAULT_PASS")}@rabbit//'
CELERY_TASK_RESULT_EXPIRES = os.environ.get("CELERY_TASK_RESULT_EXPIRES")
CELERY_ACCEPT_CONTENT = ['pickle'] #add this to your env

# EASY_THUMBNAILS settings

THUMBNAIL_DEFAULT_STORAGE = 'django.core.files.storage.FileSystemStorage'
THUMBNAIL_ALIASES = {
    '': {
        'image_40_60': {'size': (40, 60), 'crop': True},
        'image_60_90': {'size': (60, 90), 'crop': True},
        'image_80_120': {'size': (80, 120), 'crop': True},
        'image_120_180': {'size': (120, 180), 'crop': True},
        'image_160_240': {'size': (160, 240), 'crop': True},
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}

PRODUCTS_CSV_PATH = os.environ.get("PRODUCTS_CSV_PATH", "products.csv")


WAGTAILEMBEDS_FINDERS = [
    {
        "class": "wagtail.embeds.finders.oembed",
    },
    {
        "class": "blog.finders",
    },
]
