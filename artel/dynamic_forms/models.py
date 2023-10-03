import datetime

from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel, FieldRowPanel, 
    InlinePanel, MultiFieldPanel
)
from wagtail.fields import RichTextField
from wagtail.contrib.forms.models import (
    AbstractFormField, EmailFormMixin, 
    FormMixin, Page
)

from mailings.models import send_mail


class FormField(AbstractFormField):
    page = ParentalKey(
        "FormPage", related_name="form_fields", on_delete=models.CASCADE
    )


class ComfyEmailFormMixin:

    def process_form_submission(self, form):
        submission = super().process_form_submission(form)
        if self.to_address:
            self.send_mail(form)
        return submission
    
    def get_mail_subject(self):
        ...

    def send_mail(self, form):
        addresses = [x.strip() for x in self.to_address]
        send_mail(
            addresses,
            None,
            self.get_mail_subject(),
            self.render_email(form),
        )

    def render_email(self, form):
        content = []

        cleaned_data = form.cleaned_data
        for field in form:
            if field.name not in cleaned_data:
                continue

            value = cleaned_data.get(field.name)

            if isinstance(value, list):
                value = ", ".join(value)

            # Format dates and datetime(s) with SHORT_DATE(TIME)_FORMAT
            if isinstance(value, datetime.datetime):
                value = date_format(value, settings.SHORT_DATETIME_FORMAT)
            elif isinstance(value, datetime.date):
                value = date_format(value, settings.SHORT_DATE_FORMAT)

            content.append("{}: {}".format(field.label, value))

        return "\n".join(content)



class FormPage(FormMixin, Page):
    
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = FormMixin.content_panels + [
        FieldPanel('intro'),
        InlinePanel('form_fields', label="Form fields"),
        FieldPanel('thank_you_text'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel('subject'),
        ], "Email"),
    ]

    class Meta:
        abstract = True


class CustomEmailForm(ComfyEmailFormMixin, FormPage):
    template = "forms/form_page.html"
