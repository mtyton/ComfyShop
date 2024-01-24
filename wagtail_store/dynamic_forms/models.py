import datetime

from django.conf import settings
from django.db import models
from django.utils.formats import date_format
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.forms.models import (
    AbstractFormField,
    AbstractFormSubmission,
    FormMixin,
    Page,
)
from wagtail.fields import RichTextField

from dynamic_forms.forms import DynamicForm
from mailings.models import Attachment, OutgoingEmail


class Form(FormMixin, Page):
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)
    allow_attachments = models.BooleanField(default=False)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        InlinePanel("form_fields", label="Form fields"),
        FieldPanel("thank_you_text"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("from_address", classname="col6"),
                        FieldPanel("to_address", classname="col6"),
                    ]
                ),
                FieldPanel("subject"),
            ],
            "Email",
        ),
        FieldPanel("allow_attachments"),
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
    # TODO - make this optional, allow to set pattern in admin
    def get_submission_id(self, form_slug):
        case_number_daily = EmailFormSubmission.objects.filter(submit_time__date=datetime.date.today()).count()
        return f"{form_slug}-{datetime.date.today()}-{case_number_daily}"

    def send_mail(self, data):
        # modify this, get proper template
        to_addresses = data.pop("to_address").split(",")
        attachments = [
            Attachment(file.name, file.file.read(), file.content_type) for file in data.pop("attachments", [])
        ]
        subject = data.pop("subject")
        form_slug = data.pop("form_slug")
        from_address = data.pop("from_address", settings.DEFAULT_FROM_EMAIL)
        for address in to_addresses:
            OutgoingEmail.objects.send(
                subject=subject,
                template_name="form_mail",
                recipient=address,
                sender=from_address,
                context={"form_data": data, "submission_id": self.get_submission_id(form_slug)},
                attachments=attachments,
            )


class CustomEmailForm(Form):
    from_address = models.EmailField(blank=True, help_text="Sender email address")
    to_address = models.CharField(max_length=255, help_text="Comma separated list of recipients")
    subject = models.CharField(max_length=255, help_text="Subject of the email with data")

    template = "forms/email_form_page.html"

    def get_submission_class(self):
        return EmailFormSubmission

    def process_form_submission(self, form):
        attachments = form.cleaned_data.pop("attachments", [])
        submission = self.get_submission_class().objects.create(
            form_data=form.cleaned_data,
            page=self,
        )
        mail_data = form.cleaned_data.copy()
        mail_data.update(
            {
                "from_address": self.from_address,
                "to_address": self.to_address,
                "subject": self.subject,
                "attachments": attachments,
                "form_slug": self.slug,
            }
        )
        submission.send_mail(data=mail_data)
        return submission


class EmailFormField(AbstractFormField):
    form = ParentalKey("CustomEmailForm", related_name="form_fields", on_delete=models.CASCADE)
