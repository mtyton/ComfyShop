from django.db import models
from wagtail import fields
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page


class HomePage(Page):
    body = fields.RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]
