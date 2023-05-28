from .base import *

DEBUG = False

SECRET_KEY = os.environ.get("SECRET_KEY")
ALLOWED_HOSTS = [
    "localhost",
    "0.0.0.0",
    "127.0.0.1",
    "artel.tepewu.pl"
]
CSRF_TRUSTED_ORIGINS = [
    "https://0.0.0.0", "http://0.0.0.0",
    "https://localhost", "http://localhost",
    "https://artel.tepewu.pl"
]
