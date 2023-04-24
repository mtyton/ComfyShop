from django.db import models
from wagtail.models import (
    Page,
    Orderable
)
from wagtail import fields
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel
)
from modelcluster.fields import ParentalKey


class ExhibitionIndexPage(Page):
    intro = fields.RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]


class ExhibitionPage(Page):
    exhibition_desc = fields.RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('exhibition_desc'),
        InlinePanel('exhibits', label="Exhibits")
    ]


class Exhibit(Orderable):
    page = ParentalKey(ExhibitionPage, on_delete=models.CASCADE, related_name='exhibits')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    title = models.CharField(max_length=250)
    slug = models.SlugField()
    exhibit_description = models.TextField(blank=True, default="")

    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),
        FieldPanel("exhibit_description")
    ]
