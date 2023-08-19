from django.test import TestCase
from store.tests.factories import ProductTemplateFactory
from store.models import ProductTemplateImage
from django.core.files.uploadedfile import SimpleUploadedFile
from artel.tasks import generate_thumbnails
from abc import ABC


class AbstractThumbnailGenerationTest(TestCase, ABC):
    model_factory = None

    def test_generate_thumbnails(self):
        model_instance = self.model_factory()
        image_path = "media/dow.jpg"
        image_file = SimpleUploadedFile("test_image.jpg",
                                        open(image_path, "rb").read(),
                                        content_type="image/jpeg")
        instance_mock = self.model_class(
            template=model_instance,
            image=image_file,
            is_main=True
        )
        instance_mock.save()
        instance_pk = instance_mock.pk

        result = generate_thumbnails(model=instance_mock.__class__,
                                     pk=instance_pk,
                                     field="image")
        self.assertTrue(result["status"])


class ProductTemplateImageThumbnailTest(AbstractThumbnailGenerationTest):
    model_factory = ProductTemplateFactory
    model_class = ProductTemplateImage
