from django.db import models
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator
)

from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel
)
from wagtail.search import index
from modelcluster.fields import ParentalKey


class BlogPage(Page):
    create_date = models.DateField(auto_now_add=True)
    edit_date = models.DateField(auto_now=True)

    body = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel("body"),
        InlinePanel("gallery_images")
    ]


class BlogPageGalleryImage(Orderable):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    order = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1000)
        ]
    )

    panels = [
        FieldPanel('order'),
        FieldPanel('image'),
        FieldPanel('caption'),
    ]
