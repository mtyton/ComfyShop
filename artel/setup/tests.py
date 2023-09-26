from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from setup import models as setup_models
from store import SHOP_ESSENTIAL_MAIL_TEMPLATES
from mailings.models import MailTemplate


TEST_IMAGE = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
    b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
    b'\x02\x4c\x01\x00\x3b'
)


class SetupTestCase(TestCase):
    def test_get_setup_first_step_get_success(self):
        response = self.client.get(reverse('setup-page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'setup/config.html')
    
    def test_post_setup_first_step_post_success_shop_enabled(self):
        response = self.client.post(reverse('setup-page'), data={
            "logo": SimpleUploadedFile('filename.png', content=TEST_IMAGE, content_type='image/jpeg'),
            "navbar_position": setup_models.NavbarPosition.LEFT.value,
            "shop_enabled": True
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('setup-mailings'))
        self.assertEqual(setup_models.ComfyConfig.objects.count(), 1)
        config = setup_models.ComfyConfig.objects.first()
        self.assertEqual(config.navbar_position, setup_models.NavbarPosition.LEFT.value)
        self.assertEqual(config.shop_enabled, True)
        self.assertEqual(config.logo.read(), TEST_IMAGE)
        self.assertFalse(config.active)

    def test_post_setup_first_step_post_success_shop_disabled(self):
        response = self.client.post(reverse('setup-page'), data={
            "logo": SimpleUploadedFile('filename.png', content=TEST_IMAGE, content_type='image/jpeg'),
            "navbar_position": setup_models.NavbarPosition.LEFT.value,
            "shop_enabled": False
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('setup-complete'))
        self.assertEqual(setup_models.ComfyConfig.objects.count(), 1)
        config = setup_models.ComfyConfig.objects.first()
        self.assertEqual(config.navbar_position, setup_models.NavbarPosition.LEFT.value)
        self.assertEqual(config.shop_enabled, False)
        self.assertEqual(config.logo.read(), TEST_IMAGE)
        self.assertFalse(config.active)

    def test_post_setup_first_step_post_failure(self):
        response = self.client.post(reverse('setup-page'), data={
            "logo": "",
            "navbar_position": setup_models.NavbarPosition.LEFT.value,
            "shop_enabled": True
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(setup_models.ComfyConfig.objects.count(), 0)
        self.assertTemplateUsed(response, 'setup/config.html')
        self.assertFormError(response, 'form', 'logo', 'This field is required.')

    def test_get_email_config_success(self):
        response = self.client.get(reverse('setup-mailings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'setup/mailing.html')

    def test_post_email_config_success(self):
        response = self.client.post(reverse('setup-mailings'), data={
                key: SimpleUploadedFile(
                    f'{key}.html', content=b'<html></html>', content_type='text/html'
                ) for key, _ in SHOP_ESSENTIAL_MAIL_TEMPLATES.items()
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('setup-complete'))
        self.assertEqual(MailTemplate.objects.count(), 3)
        self.assertEqual(MailTemplate.objects.filter(template_name__in=SHOP_ESSENTIAL_MAIL_TEMPLATES.keys()).count(), 3)

    def test_post_email_config_failure(self):
        response = self.client.post(reverse('setup-mailings'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(MailTemplate.objects.count(), 0)
        self.assertTemplateUsed(response, 'setup/mailing.html')
        self.assertFormError(response, 'form', None, None, 'This field is required.')
