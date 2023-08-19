from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from store.tests.factories import ProductTemplateFactory
from store.models import ProductTemplateImage
from abc import ABC


class AbstractSignalTest(TestCase, ABC):
    def setUp(self):
        self.template_instance = ProductTemplateFactory()

    def create_instance_mock(self):
        raise NotImplementedError("Subclasses must implement this method")

    @patch("artel.tasks.generate_thumbnails.delay")
    def test_generate_thumbnails_async_signal(self, mock_generate_thumbnails):
        self.instance_mock = self.create_instance_mock()

        mock_generate_thumbnails.assert_called_once_with(
            model=self.instance_mock.__class__,
            pk=self.instance_mock.pk,
            field="image",
        )


class ProductTemplateImageSignalTest(AbstractSignalTest):
    def create_instance_mock(self):
        return ProductTemplateImage.objects.create(
            template=self.template_instance,
            image=SimpleUploadedFile("test_image.jpg", b"fake_content"),
            is_main=True
        )
