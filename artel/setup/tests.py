import json
import os

from django.test import TestCase
from django.urls import reverse

from setup.forms import SiteConfigurationForm, SkinChangerForm
from setup.models import generate_css_content


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
            'navbar_position': 'left',
            'skin': 'dark',
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
            self.assertEqual(json_data['skin'], 'dark')
        os.remove('config.json')

    def test_post_invalid_form(self):
        form_data = {}
        response = self.client.post(reverse('setup'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(os.path.exists('config.json'))


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
    def test_config_context_processor(self):
        from django.conf import settings
        settings.NAVBAR_POSITION = 'left'
        settings.LOGO = 'media/images/icons/logo.png'
        settings.SHOP_ENABLED = True
        settings.SKIN = 'none'

        response = self.client.get(reverse('setup'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['navbar_position'], 'left')
        self.assertEqual(response.context['logo_url'], 'media/images/icons/logo.png')
        self.assertTrue(response.context['shop_enabled'])
        self.assertEqual(response.context['skin'], 'none')


class SkinChangerViewTest(TestCase):
    def test_get_request(self):
        if not os.path.exists('config.json'):
            with open('config.json', 'w') as file:
                file.write('{}')
        response = self.client.get(reverse('skin'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'skin_changer.html')
        self.assertIsInstance(response.context['form'], SkinChangerForm)
        os.remove('config.json')

    def test_post_request_with_valid_form(self):
        if not os.path.exists('config.json'):
            with open('config.json', 'w') as file:
                file.write('{}')
        form_data = {
            'background_color': '#FFFFFF',
            'font_color': '#000000',
            'hr_color': '#FFFFFF',
            'link_color': '#000000',
            'hover_on_link_color': '#FFFFFF',
        }
        response = self.client.post(reverse('skin'), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        os.remove('config.json')

    def test_post_request_with_invalid_form(self):
        if not os.path.exists('config.json'):
            with open('config.json', 'w') as file:
                file.write('{}')
        form_data = {}
        response = self.client.post(reverse('skin'), form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'skin_changer.html')
        self.assertIsInstance(response.context['form'], SkinChangerForm)
        os.remove('config.json')


class GenerateCSSContentTest(TestCase):
    def test_generate_css_content(self):
        form_data = {
            'background_color': '#FFFFFF',
            'font_color': '#000000',
            'hr_color': '#FFFFFF',
            'link_color': '#000000',
            'hover_on_link_color': '#FFFFFF',
        }
        expected_css_content = """
        body {
            background-color: #FFFFFF;
            color: #000000;
        }

        hr {
            background-color: #FFFFFF;
        }

        a[href] {
            color: #000000;
        }

        a[href]:hover {
            color: #FFFFFF;
        }
    """
        css_content = generate_css_content(form_data)
        self.assertEqual(css_content, expected_css_content)
