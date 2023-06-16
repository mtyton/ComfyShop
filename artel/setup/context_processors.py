from .models import SiteConfiguration
from django.conf import settings


def logo_url(request):
    config = SiteConfiguration.objects.first()
    if config.logo:
        logo_url = config.logo.url
    else:
        None
    return {'logo_url': logo_url}


def menu_position(request):
    config = SiteConfiguration.objects.first()
    if config.navbar_position == 'left':
        menu_left = True
    else:
        menu_left = False
    return {'menu_left': menu_left}


def store_enabled(request):
    store_enabled = getattr(settings, 'SHOP_ENABLED', False)
    return {'store_enabled': store_enabled}
