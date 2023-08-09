from django.db.models.signals import post_save
from django.dispatch import receiver
from store.models import ProductTemplateImage
from artel.tasks import generate_thumbnails


@receiver(post_save, sender=ProductTemplateImage)
def generate_thumbnail(sender, instance, **kwargs):
    image_path = instance.image.path
    generate_thumbnails.delay(image_path)
