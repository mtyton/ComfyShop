import logging
from django.shortcuts import redirect

from setup.models import ComfyConfig

logger = logging.getLogger(__name__)


class CheckSetupMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        config = None
        try:
            config = ComfyConfig.objects.get()
        except ComfyConfig.DoesNotExist:
            if not request.path_info.startswith('/setup'):
                return redirect('/setup/')
        except ComfyConfig.MultipleObjectsReturned:
            config = ComfyConfig.objects.first()
            logger.exception("Multiple ComfyConfig objects found. Using first one.")
        
        if config and request.path_info.startswith('/setup'):
            return redirect('/')
        
        response = self.get_response(request)
        return response
