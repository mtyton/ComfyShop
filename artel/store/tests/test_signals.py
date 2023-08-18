from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from store.tests.factories import ProductTemplateFactory
from store.models import ProductTemplateImage


class SignalTest(TestCase):
    @patch("artel.tasks.generate_thumbnails.delay")
    def test_generate_thumbnails_async_signal(self, mock_generate_thumbnails):
        template_instance = ProductTemplateFactory()

        instance_mock = ProductTemplateImage.objects.create(
            template=template_instance,
            image=SimpleUploadedFile("test_image.jpg", b"fake_content"),
            is_main=True
        )

        mock_generate_thumbnails.assert_called_once_with(
            model=instance_mock.__class__,
            pk=instance_mock.pk,
            field="image",
        )
