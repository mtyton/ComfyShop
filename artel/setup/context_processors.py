from django.conf import settings


def SetupContextProcessor(request):
    navbar_position = settings.NAVBAR_POSITION
    logo = settings.LOGO
    shop_enabled = settings.SHOP_ENABLED
    skin = settings.SKIN
    return {
            'navbar_position': navbar_position,
            'logo_url': logo,
            'shop_enabled': shop_enabled,
            'skin': skin,
        }
