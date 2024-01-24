import logging
from dataclasses import dataclass
from typing import Any

from django.conf import settings
from django.core.mail import EmailMessage
from django.db import models, transaction
from django.template import Context, Template

logger = logging.getLogger(__name__)


@dataclass
class Attachment:
    name: str
    content: Any
    contenttype: str


def send_mail(
    to: list[str],
    attachments: list[Attachment],
    subject: str,
    content: str,
    sender_email: str = settings.DEFAULT_FROM_EMAIL,
):
    message = EmailMessage(subject=subject, body=content, from_email=sender_email, to=to)
    message.content_subtype = "html"
    for attachment in attachments:
        message.attach(attachment.name, attachment.content, attachment.contenttype)

    sent = bool(message.send())
    if not sent:
        logger.exception(f"Sending email to {to} with subject {subject} caused an exception")
    return sent


class MailTemplate(models.Model):
    template_name = models.CharField(max_length=255, unique=True)

    template = models.FileField(upload_to="mail_templates")

    def delete(self, *args, **kwargs):
        # delete file
        super().delete(*args, **kwargs)

        @transaction.on_commit
        def remove_template_file(self):
            self.template.delete()

    def load_and_process_template(self, context: dict | Context):
        if not self.template:
            logger.exception(
                f"Template file is missing for template with " + f"pk={self.pk}, template_name={self.template_name}"
            )
            raise FileNotFoundError("Template file is missing")
        if isinstance(context, dict):
            context = Context(context)
        with open(self.template.path, "r", encoding="utf-8") as f:
            content = f.read()
        template = Template(content)
        return template.render(context)


class OutgoingEmailManager(models.Manager):
    def send(
        self,
        template_name: str,
        subject: str,
        recipient: str,
        context: dict | Context,
        sender: str,
        attachments: list[Attachment] = None,
    ):
        template = MailTemplate.objects.get(template_name=template_name)
        outgoing_email = self.create(template=template, recipient=recipient, subject=subject, sender=sender)
        attachments = attachments or []
        # send email
        sent = send_mail(
            to=[recipient],
            sender_email=sender,
            subject=subject,
            content=template.load_and_process_template(context),
            attachments=attachments,
        )
        outgoing_email.sent = sent
        outgoing_email.save()
        return outgoing_email


class OutgoingEmail(models.Model):
    subject = models.CharField(max_length=255)
    template = models.ForeignKey(MailTemplate, on_delete=models.CASCADE)
    sender = models.EmailField()
    recipient = models.EmailField()

    sent = models.BooleanField(default=False)

    objects = OutgoingEmailManager()
