import datetime

from django.db import models
from django.conf import settings
from django.utils.formats import date_format

from modelcluster.fields import ParentalKey
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
from dynamic_forms.forms import DynamicForm


class Form(FormMixin, Page):
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
        FieldPanel("allow_attachments")
    ]

    def get_form_class(self):
        return DynamicForm
    
    def get_form(self, *args, **kwargs):
        form_class = self.get_form_class()
        form_params = self.get_form_parameters()
        form_params.update(kwargs)
        form_params["field_list"] = self.get_form_fields()
        form_params["file_uploads"] = self.allow_attachments
        return form_class(*args, **form_params)

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

            content.append("{}: {}".format(field_name, value))

        return "\n".join(content)
    
    def send_mail(self, data):
        to_addresses = data.pop("to_address").split(",")
        subject = data.pop("subject")
        from_address = data.pop("from_address", settings.DEFAULT_FROM_EMAIL)
        addresses = [x.strip() for x in to_addresses]
        send_mail(
            addresses,
            [],
            subject,
            self.render_email(data),
            from_address
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

    def get_submission_class(self):
        return EmailFormSubmission

    def process_form_submission(self, form):
        submission = self.get_submission_class().objects.create(
            form_data=form.cleaned_data,
            page=self,
        )
        mail_data = form.cleaned_data.copy()
        mail_data.update({
            "from_address": self.from_address,
            "to_address": self.to_address,
            "subject": self.subject
        })
        submission.send_mail(data=mail_data)
        return submission

class EmailFormField(AbstractFormField):
    form = ParentalKey(
        "CustomEmailForm", related_name="form_fields", on_delete=models.CASCADE
    )
