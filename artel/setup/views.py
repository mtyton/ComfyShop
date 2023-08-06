from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
import os
from .forms import SiteConfigurationForm, SkinChangerForm
import json


class SetupPageView(View):
    template_name = 'setup.html'

    def get(self, request):
        form = SiteConfigurationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = SiteConfigurationForm(request.POST, request.FILES)
        if form.is_valid():
            form_data = form.cleaned_data
            logo_path = form.save_logo()
            if logo_path:
                form_data['logo'] = 'media/' + logo_path
            else:
                form_data['logo'] = None

            json_data = json.dumps(form_data, indent=4)
            with open('config.json', 'w') as file:
                file.write(json_data)

            if form_data['skin'] == 'custom':
                return redirect('/skins')

            return redirect('/')
        else:
            return render(request, self.template_name, {'form': form})


class SkinChangerView(View):
    template_name = 'skin_changer.html'

    def get(self, request):
        form = SkinChangerForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = SkinChangerForm(request.POST)
        if form.is_valid():
            form_data = form.data
            if form_data:
                css_content = generate_css_content(form_data)
                file_name = 'custom.css'
                css_file_path = os.path.join(settings.MEDIA_ROOT, 'css', file_name)
                with open(css_file_path, 'w') as css_file:
                    css_file.write(css_content)
                return redirect('/')
            return render(request, self.template_name, {'form': form})


def generate_css_content(form_data):
    css_content = f"""
        body {{
            background-color: {form_data['background_color']};
            color: {form_data['font_color']};
        }}

        hr {{
            background-color: {form_data['hr_color']};
        }}

        a[href] {{
            color: {form_data['link_color']};
        }}

        a[href]:hover {{
            color: {form_data['hover_on_link_color']};
        }}
    """
    return css_content
