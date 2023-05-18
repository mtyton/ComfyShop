from .base import *

DEBUG = False

SECRET_KEY = os.environ.get("SECRET_KEY")
ALLOWED_HOSTS = [
    "http://91.195.93.3",
    "https://91.195.93.3",
    "localhost",
    "0.0.0.0",
    "127.0.0.1"
]
CSRF_TRUSTED_ORIGINS = ['http://91.195.93.3:8001', 'http://91.195.93.3']
