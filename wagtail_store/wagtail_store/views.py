from django.conf import settings
from django.http import HttpResponseNotFound
from sentry_sdk import capture_message


def my_custom_page_not_found_view(*args, **kwargs):
    if settings.SENTRY_ENVIRONMENT != 'production':
        capture_message("Page not found!", level="error")

    # return any response here, e.g.:
    return HttpResponseNotFound("Not found")
