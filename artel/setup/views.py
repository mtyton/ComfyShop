from django.shortcuts import render, redirect
from django.views import View
from .forms import SiteConfigurationForm
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

            return redirect('/')
        else:
            return render(request, self.template_name, {'form': form})
