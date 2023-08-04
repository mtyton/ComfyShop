from celery import shared_task
from easy_thumbnails.files import get_thumbnailer


@shared_task
def generate_thumbnails(image_instance):
    thumbnailer = get_thumbnailer(image_instance)
    small_thumbnail = thumbnailer.get_thumbnail({'size': (40, 60), 'crop': False})
    medium_thumbnail = thumbnailer.get_thumbnail({'size': (80, 120), 'crop': False})
    large_thumbnail = thumbnailer.get_thumbnail({'size': (160, 240), 'crop': False})

    return {
        'small': small_thumbnail.url,
        'medium': medium_thumbnail.url,
        'large': large_thumbnail.url,
    }
