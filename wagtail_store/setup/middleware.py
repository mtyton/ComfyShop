import logging
from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpResponse

from store.models import ProductListPage
from setup.models import ComfyConfig

logger = logging.getLogger(__name__)


class CheckSetupMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        config = None
        try:
            config = ComfyConfig.objects.get(active=True)
        except ComfyConfig.DoesNotExist:
            if (not request.path_info.startswith('/setup') and not request.path_info.startswith('/admin')
                and not request.path_info.startswith('/media') and not request.path_info.startswith('/static')):
                return redirect('/setup/')
        except ComfyConfig.MultipleObjectsReturned:
            config = ComfyConfig.objects.first()
            logger.exception("Multiple ComfyConfig objects found. Using first one.")
        
        if config and request.path_info.startswith('/setup'):
            return redirect('/')
        
        response = self.get_response(request)
        return response


class CheckShopMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def _check_if_store_request(self, request):
        if request.path_info.startswith('/store-app/'):
            return True
        if request.path_info == "/":
            return False
        return ProductListPage.objects.filter(url_path__endswith=request.path_info).exists()

    def __call__(self, request):
        config = ComfyConfig.objects.filter(active=True).first()
        if config and not config.shop_enabled and self._check_if_store_request(request):
            if settings.DEBUG:
                return HttpResponse(
                    status=500, content="Store is not enabled please turn it on in admin panel"
                )
            else:
                return redirect('/')
        
        response = self.get_response(request)
        return response
