import logging
import celery
from django.conf import settings
from easy_thumbnails.files import generate_all_aliases

from mailings.models import OutgoingEmail
from store.models import Product
from store.admin import ProductAdmin


logger = logging.getLogger(__name__)


@celery.shared_task(name="send_produt_request_email")
def send_produt_request_email(variant_pk: int):
    try:
        variant = Product.objects.get(pk=variant_pk)
    except Product.DoesNotExist:
        logger.exception(f"Product with pk={variant_pk} does not exist")

    try:
        admin_url = ProductAdmin().url_helper.get_action_url("edit", variant.pk)
        send = OutgoingEmail.objects.send(
            template_name="product_request",
            subject="Złożono zapytanie ofertowe",
            recipient=variant.template.author.email,
            context={"product": variant, "admin_url": admin_url},
            sender=settings.DEFAULT_FROM_EMAIL
        )
    except Exception as e:
        logger.exception(f"Could not send email for variant pk={variant_pk}, exception: {e} has occured")
    else:    
        if not send:
            logger.exception(f"Could not send email for variant pk={variant_pk}")
