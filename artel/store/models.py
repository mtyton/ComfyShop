from django.db import models
from django.core.paginator import (
    Paginator,
    EmptyPage
)
from django.conf import settings

from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel
)
from wagtail.models import Page
from wagtail import fields as wagtail_fields
from taggit.managers import TaggableManager


class ProductAuthor(models.Model):
    name = models.CharField(max_length=255)
    # TODO - add author contact data

    def __str__(self):
        return self.name


class ProductCategory(ClusterableModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    panels = [
        FieldPanel("name"),
        InlinePanel("category_params")
    ]


class CategoryParamTypeChoices(models.TextChoices):
    INT = "int"
    STRING = "str"
    FLOAT = "float"


class ProductCategoryParam(ClusterableModel):
    category = ParentalKey(ProductCategory, on_delete=models.CASCADE, related_name="category_params")
    key = models.CharField(max_length=200)
    param_type = models.CharField(max_length=200, choices=CategoryParamTypeChoices.choices)

    def __str__(self):
        return self.key


class ProductTemplate(ClusterableModel):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    author = models.ForeignKey(ProductAuthor, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    description = models.TextField()

    tags = TaggableManager()
    
    def __str__(self):
        return self.title

    panels = [
        FieldPanel("category"),
        FieldPanel("author"),
        FieldPanel('title'),
        FieldPanel('code'),
        FieldPanel('description'),
        InlinePanel("images"),
        FieldPanel("tags"),
    ]


class ProductImage(models.Model):
    template = ParentalKey(
        ProductTemplate, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField()


class Product(ClusterableModel):
    template = models.ForeignKey(ProductTemplate, on_delete=models.CASCADE, related_name="products")
    price = models.FloatField()
    available = models.BooleanField(default=True)

    panels = [
        FieldPanel("template"),
        FieldPanel("price"),
        InlinePanel("param_values"),
        FieldPanel("available")
    ]

    @property
    def main_image(self):
        images = self.template.images.all()
        print(images)
        if images:
            return images.first().image

    @property
    def title(self):
        return f"{self.template.title} - {self.price}"


class TemplateParamValue(models.Model):
    param = models.ForeignKey(ProductCategoryParam, on_delete=models.CASCADE)
    product = ParentalKey(Product, on_delete=models.CASCADE, related_name="param_values")
    value = models.CharField(max_length=255)


class ProductListPage(Page):
    # TODO add filters

    description = wagtail_fields.RichTextField(blank=True)
    tags = TaggableManager(blank=True)

    def _get_items(self):
        if self.tags.all():
            return Product.objects.filter(available=True, template__tags__in=self.tags.all())
        return Product.objects.filter(available=True)

    def get_context(self, request):
        context = super().get_context(request)
        items = self._get_items()
        if not items:
            return context
        
        paginator = Paginator(items, settings.PRODUCTS_PER_PAGE)
        page_number = request.GET.get("page", 1)
        try:
            page = paginator.page(page_number)
        except EmptyPage:
            page = paginator.page(1)
        context["items"] = page.object_list
        context["page"] = page
        return context

    content_panels = Page.content_panels + [
        FieldPanel("description"),
        FieldPanel("tags")
    ]
