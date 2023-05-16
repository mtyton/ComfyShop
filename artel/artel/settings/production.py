from .base import *

DEBUG = False

SECRET_KEY = os.environ.get("SECRET_KEY")
ALLOWED_HOSTS = [
    "91.195.93.3",
    "localhost",
    "0.0.0.0",
    "127.0.0.1"
]
