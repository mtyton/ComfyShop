from django.db import models
from django.core.paginator import (
    Paginator,
    EmptyPage
)
from django.conf import settings
from django.core.validators import MinValueValidator

from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel
)
from wagtail.models import Page
from wagtail import fields as wagtail_fields
from taggit.managers import TaggableManager
from phonenumber_field.modelfields import PhoneNumberField


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
    description = models.TextField(blank=True)

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
    name = models.CharField(max_length=255, blank=True)
    info = models.TextField(blank=True)
    template = models.ForeignKey(ProductTemplate, on_delete=models.CASCADE, related_name="products")
    price = models.FloatField()
    available = models.BooleanField(default=True)

    panels = [
        FieldPanel("template"),
        FieldPanel("price"),
        InlinePanel("param_values"),
        FieldPanel("available"),
        FieldPanel("name"),
        FieldPanel("info")
    ]

    @property
    def main_image(self):
        images = self.template.images.all()
        print(images)
        if images:
            return images.first().image

    @property
    def tags(self):
        return self.template.tags.all()

    @property
    def description(self):
        return self.info or self.template.description

    @property
    def title(self):
        return self.name or self.template.title


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

class CustomerData(models.Model):
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    email = models.EmailField()
    phone = PhoneNumberField()
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=120)
    country = models.CharField(max_length=120)

    @property
    def full_name(self):
        return f"{self.name} {self.surname}"
    
    @property
    def full_address(self):
        return f"{self.street}, {self.zip_code} {self.city}, {self.country}"


class OrderProductManager(models.Manager):
    def create_from_cart(self, cart, order):
        for item in cart:
            self.create(
                product=item.product,
                order=order,
                quantity=item.quantity
            )


class OrderProduct(models.Model):   
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="products")
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    objects = OrderProductManager()


class Order(models.Model):
    customer = models.ForeignKey(CustomerData, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent = models.BooleanField(default=False)
