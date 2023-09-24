from django.test import TestCase

from setup.models import ComfyConfig


class BaseComfyTestCaseMixin:
    def setUp(self):
        ComfyConfig.objects.create(
            logo="images/logo.png",
            navbar_position="left",
            shop_enabled=True,
            active=True,
        )
        super().setUp()
