import datetime

from django.db import models
from django.conf import settings
from django.utils.formats import date_format

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    FieldPanel, FieldRowPanel, 
    InlinePanel, MultiFieldPanel
)
from wagtail.fields import RichTextField
from wagtail.contrib.forms.models import (
    AbstractFormField,
    FormMixin,
    Page,
    AbstractFormSubmission
)

from mailings.models import send_mail


class Form(FormMixin, ClusterableModel):
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)
    allow_attachments = models.BooleanField(default=False)
    
    content_panels = Page.content_panels + [
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


class EmailFormSubmission(AbstractFormSubmission):
    def render_email(self, data):
        content = []
        for field_name, value in data.items():
            if isinstance(value, list):
                value = ", ".join(value)

            # Format dates and datetime(s) with SHORT_DATE(TIME)_FORMAT
            if isinstance(value, datetime.datetime):
                value = date_format(value, settings.SHORT_DATETIME_FORMAT)
            elif isinstance(value, datetime.date):
                value = date_format(value, settings.SHORT_DATE_FORMAT)

            content.append("{}: {}".format(field_name.label, value))

        return "\n".join(content)
    
    def send_mail(self, data):
        addresses = [x.strip() for x in data["to_address"].split(",")]
        send_mail(
            addresses,
            [],
            data.pop("subject"),
            self.render_email(data),
            data.pop("from_address", settings.DEFAULT_FROM_EMAIL)
        )


class CustomEmailForm(Form):
    from_address = models.EmailField(
        blank=True,
        help_text="Sender email address"
    )
    to_address = models.CharField(
        max_length=255,
        help_text="Comma separated list of recipients"
    )
    subject = models.CharField(
        max_length=255,
        help_text="Subject of the email with data"
    )

    template = "forms/email_form_page.html"


class EmailFormField(AbstractFormField):
    form = ParentalKey(
        "CustomEmailForm", related_name="form_fields", on_delete=models.CASCADE
    )
