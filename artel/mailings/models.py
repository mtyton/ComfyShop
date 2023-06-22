from typing import Any
from dataclasses import dataclass

from django.db import models
from django.db import transaction
from django.template import (
    Template,
    Context
)
from django.core.mail import EmailMessage
from django.conf import settings


@dataclass
class Attachment:
    name: str
    content: Any
    contenttype: str


def send_mail(
        to: list[str], 
        attachments: list[Attachment],
        subject: str, 
        body: str,
        sender_email: str = settings.DEFAULT_FROM_EMAIL
    ):
    message = EmailMessage(
        subject=subject,
        body=body,
        from_email=sender_email,
        to=to
    )
    for attachment in attachments:
        message.attach(attachment.name, attachment.content, attachment.contenttype)
    return bool(message.send())


class MailTemplate(models.Model):
    template_name = models.CharField(max_length=255, unique=True)

    template = models.FileField(
        upload_to="mail_templates"
    )
    subject = models.CharField(max_length=255)

    def delete(self, *args, **kwargs):
        # delete file
        super().delete(*args, **kwargs)
        
        @transaction.on_commit
        def remove_template_file(self):
            self.template.delete()

    def load_and_process_template(self, context: dict|Context):
        if not self.template:
            raise FileNotFoundError("Template file is missing")
        if isinstance(context, dict):
            context = Context(context)
        with open(self.template.path, "r", encoding="utf-8") as f:
            content = f.read()
        template = Template(content)
        return template.render(context)


class OutgoingEmailManager(models.Manager):

    def send(
            self, template_name: str, 
            recipient: str, context: dict | Context, 
            sender:str,  attachments: list[Attachment] = None
        ):
        template = MailTemplate.objects.get(template_name=template_name)
        outgoing_email = self.create(template=template, recipient=recipient)
        attachments = attachments or []
        # send email
        sent = send_mail(
            to=[recipient], sender_email=sender,
            subject=template.subject, content=template.load_and_process_template(context),
            attachments=attachments
        )
        outgoing_email.sent = sent
        outgoing_email.save()
        return outgoing_email


class OutgoingEmail(models.Model):
    template = models.ForeignKey(MailTemplate, on_delete=models.CASCADE)
    sender = models.EmailField()
    recipient = models.EmailField()

    sent = models.BooleanField(default=False)

    objects = OutgoingEmailManager()
