from django.test import TestCase
from django.urls import reverse
import json
import os

from .forms import SiteConfigurationForm


class SetupPageViewTestCase(TestCase):
    def test_get(self):
        response = self.client.get(reverse('setup'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], SiteConfigurationForm)

    def test_post_valid_form(self):
        logo_path = '/app/artel/static/images/icons/las_ruinas_PL.png'
        logo_file = open(logo_path, 'rb')
        form_data = {
            'logo': logo_file,
            'shop_enabled': False,
            'navbar_position': 'left'
        }
        response = self.client.post(reverse('setup'), data=form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(os.path.exists('config.json'))
        self.assertRedirects(response, '/')

        with open('config.json') as file:
            json_data = json.load(file)
            self.assertEqual(json_data['logo'], 'media/images/icons/las_ruinas_PL.png')
            self.assertFalse(json_data['shop_enabled'])
            self.assertEqual(json_data['navbar_position'], 'left')
        os.remove('config.json')

    def test_post_invalid_form(self):
        form_data = {}
        response = self.client.post(reverse('setup'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(os.path.exists('config.json'))
        self.assertContains(response, 'This field is required')


class CheckSetupMiddlewareTestCase(TestCase):
    def test_setup_page_redirect(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/setup/')

    def test_existing_config_redirect(self):
        with open('config.json', 'w') as file:
            file.write('{}')

        response = self.client.get(reverse('setup'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        os.remove('config.json')


class SetupContextProcessorTestCase(TestCase):
    def test_setup_context_processor(self):
        from django.conf import settings
        settings.NAVBAR_POSITION = 'left'
        settings.LOGO = 'media/images/icons/logo.png'
        settings.SHOP_ENABLED = True

        response = self.client.get(reverse('setup'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['navbar_position'], 'left')
        self.assertEqual(response.context['logo_url'], 'media/images/icons/logo.png')
        self.assertTrue(response.context['shop_enabled'])
