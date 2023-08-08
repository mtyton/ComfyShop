from django.db.models.signals import post_save
from django.dispatch import receiver
from store.models import ProductTemplateImage
from artel.tasks import generate_thumbnails


@receiver(post_save, sender=ProductTemplateImage)
def create_thumbnail_on_image_creation(sender, instance, created, **kwargs):
    if created:
        generate_thumbnails.delay(instance.image.url)
