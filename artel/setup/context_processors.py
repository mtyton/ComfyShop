from django.conf import settings

from setup.models import ComfyConfig
from setup.serializers import ConfigSerializers


def config_context_processor(request):
    config = ComfyConfig.objects.filter(active=True).first()
    serializer = ConfigSerializers(instance=config)
    return serializer.data
