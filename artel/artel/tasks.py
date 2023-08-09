from celery import shared_task
from easy_thumbnails.files import get_thumbnailer
import logging


logger = logging.getLogger(__name__)

THUMBNAIL_SIZES = {
    'image_40_60': (40, 60, True),
    'image_60_90': (60, 90, True),
    'image_80_120': (80, 120, True),
    'image_120_180': (120, 180, True),
    'image_160_240': (160, 240, True),
}


@shared_task
def generate_thumbnails(image_path):
    try:
        thumbnailer = get_thumbnailer(image_path)
        thumbnails = {}
        for size_name, (width, height, crop) in THUMBNAIL_SIZES.items():
            thumbnail = thumbnailer.get_thumbnail({'size': (width, height), 'crop': crop})
            thumbnails[size_name] = thumbnail.url
        return thumbnails
    except Exception as e:
        logger.exception(f"Error generating thumbnails for image_instance {image_path}: {e}")
        return None
