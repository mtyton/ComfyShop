from .base import *

DEBUG = False

SECRET_KEY = os.environ.get("SECRET_KEY")
ALLOWED_HOSTS = [
    "91.195.93.3",
    "91.195.93.3:8001",
    "localhost",
    "0.0.0.0",
    "127.0.0.1"
]
CSRF_TRUSTED_ORIGINS = ['91.195.93.3:8001', '91.195.93.3']
