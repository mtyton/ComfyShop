import logging
import typing

from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.views import View

from setup.forms import MailTemplatesFileUploadForm, SiteConfigurationForm
from setup.models import ComfyConfig

logger = logging.getLogger(__name__)


class BaseSetupView(View):
    tempalte_name = None
    form_class = None
    next_step_view = None
    step = None

    def get_context_data(self):
        return {"form": self.form_class()}

    def get(self, request):
        return render(request, self.template_name, self.get_context_data())

    def handle_posted_form(self, request: HttpRequest):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            return form.save(), {}
        context = self.get_context_data()
        context["form"] = form
        return None, context

    def get_redirect(self, form_result: typing.Any = None):
        return redirect(self.next_step_view)

    def post(self, request: HttpRequest):
        form_result, ctx = self.handle_posted_form(request)
        if form_result:
            return self.get_redirect(form_result)

        return render(request, self.template_name, ctx)


class SetupPageView(BaseSetupView):
    template_name = "setup/config.html"
    next_step_view = "setup-mailings"
    form_class = SiteConfigurationForm
    step = 1

    def get_redirect(self, form_result: typing.Any = None):
        if form_result.shop_enabled:
            return super().get_redirect(form_result)
        return redirect("setup-complete")

    def handle_posted_form(self, request: HttpRequest):
        result, ctx = super().handle_posted_form(request)
        if not result:
            return result, ctx

        request.session["config_id"] = result.id
        return result, ctx


class SetupMailingView(BaseSetupView):
    template_name = "setup/mailing.html"
    next_step_view = "setup-complete"
    form_class = MailTemplatesFileUploadForm
    step = 2


class SetupCompleteView(BaseSetupView):
    template_name = "setup/complete.html"
    step = 3

    def _get_config(self, request: HttpRequest):
        config_id = request.session.get("config_id", None)
        if config_id is None:
            return redirect("setup-page")

        return ComfyConfig.objects.get(id=config_id)

    def get_context_data(self):
        return {"config": self._get_config(self.request)}

    def post(self, request: HttpRequest):
        config = self._get_config(request)
        config.active = True
        config.save()

        request.session.flush()
        return redirect("/")
