from django.shortcuts import render, redirect
from .models import SiteConfiguration
from .forms import SiteConfigurationForm
import json


def setup_page(request):
    config = SiteConfiguration.objects.first()

    if request.method == 'POST':
        form = SiteConfigurationForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            form_data = form.cleaned_data
            form_data['logo'] = str(form_data['logo'])

            json_data = json.dumps(form_data, indent=4)

            with open('config.json', 'w') as file:
                file.write(json_data)

            return redirect('/')
    else:
        form = SiteConfigurationForm(instance=config)

    return render(request, 'setup.html', {'form': form})
