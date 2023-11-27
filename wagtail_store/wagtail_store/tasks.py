import celery
import logging

from easy_thumbnails.files import generate_all_aliases


logger = logging.getLogger(__name__)


@celery.shared_task(name="generate_thumbnails")
def generate_thumbnails(model, pk, field):
    try:
        instance = model._default_manager.get(pk=pk)
        fieldfile = getattr(instance, field)
        generate_all_aliases(fieldfile, include_global=True)
        return {"status": True}
    except Exception as e:
        logger.exception("An error occurred while generating thumbnails.")
        return {"status": False, "error": str(e)}
