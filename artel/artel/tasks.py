from celery import shared_task
from easy_thumbnails.files import generate_all_aliases
import logging


logger = logging.getLogger(__name__)


@shared_task(serializer="pickle")
def generate_thumbnails(model, pk, field):
    try:
        instance = model._default_manager.get(pk=pk)
        fieldfile = getattr(instance, field)
        generate_all_aliases(fieldfile, include_global=True)
        return {"status": True}
    except Exception as e:
        logger.exception("An error occurred while generating thumbnails.")
        return {"status": False, "error": str(e)}
