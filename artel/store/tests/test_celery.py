from django.test import TestCase
from unittest.mock import patch
from store.tests.factories import ProductTemplateFactory
from store.models import ProductTemplateImage
from django.core.files.uploadedfile import SimpleUploadedFile
from artel.tasks import generate_thumbnails


class CeleryTaskTest(TestCase):
    @patch('artel.tasks.generate_thumbnails')
    def test_generate_thumbnails(self, mock_generate_thumbnails):
        template_instance = ProductTemplateFactory()
        image_path = "media/dow.jpg"
        image_file = SimpleUploadedFile("test_image.jpg",
                                        open(image_path, "rb").read(),
                                        content_type="image/jpeg")
        instance_mock = ProductTemplateImage(
            template=template_instance,
            image=image_file,
            is_main=True
        )
        instance_mock.save()
        instance_pk = instance_mock.pk

        result = generate_thumbnails(model=instance_mock.__class__,
                                     pk=instance_pk,
                                     field="image")
        self.assertTrue(result["status"])
