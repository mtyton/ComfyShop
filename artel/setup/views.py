from django.shortcuts import (
    render,
    redirect
)
from django.views import View

from setup.forms import SiteConfigurationForm


class SetupPageView(View):
    template_name = 'setup/config.html'

    def get_context_data(self, **kwargs):
        return {
            "form": SiteConfigurationForm()
        }

    def get(self, request):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request):
        form = SiteConfigurationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('wagtailadmin_home')
        
        context = self.get_context_data()
        context['form'] = form
        return render(request, self.template_name, context)
