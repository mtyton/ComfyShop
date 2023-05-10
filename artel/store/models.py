from django.db import models

from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel
)
from wagtail.models import Orderable


class ProductAuthor(models.Model):
    name = models.CharField(max_length=255)

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
    
    def __str__(self):
        return self.title

    def get_images(self):
        return self.images.objects.all().values_list("image")

    panels = [
        FieldPanel("category"),
        FieldPanel("author"),
        FieldPanel('title'),
        FieldPanel('code'),
        FieldPanel('description'),
        InlinePanel("images")
    ]


class ProductImage(models.Model):
    template = ParentalKey(
        ProductTemplate, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField()


class Product(ClusterableModel):
    template = models.ForeignKey(ProductTemplate, on_delete=models.CASCADE)
    price = models.FloatField()

    panels = [
        FieldPanel("template"),
        FieldPanel("price"),
        InlinePanel("param_values")
    ]

    @property
    def title(self):
        return f"{self.template.title} - {self.price}"


class TemplateParamValue(models.Model):
    param = models.ForeignKey(ProductCategoryParam, on_delete=models.CASCADE)
    product = ParentalKey(Product, on_delete=models.CASCADE, related_name="param_values")
    value = models.CharField(max_length=255)
