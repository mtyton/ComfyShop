import pdfkit
from django.db import models
from django.core.paginator import (
    Paginator,
    EmptyPage
)
from django.conf import settings
from django.core.validators import MinValueValidator
from django.template import (
    Template,
    Context
)

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

from store.utils import (
    send_mail
)


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
        for item in cart.get_items():
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


class OrderManager(models.Manager):
    def create_from_cart(self, cart, customer_data):
        order = self.create(customer=customer_data)
        OrderProduct.objects.create_from_cart(cart, order)
        # create proper documents
        # NOTE - this is temporary
        # agreement_template = DocumentTemplate.objects.filter(
        #     doc_type=DocumentTypeChoices.AGREEMENT
        # ).order_by("-created_at").first()
        # receipt_template = DocumentTemplate.objects.filter(
        #     doc_type=DocumentTypeChoices.RECEIPT
        # ).order_by("-created_at").first()
        # agreement = OrderDocument.objects.create(
        #     order=order,
        #     template=agreement_template
        # )
        # receipt = OrderDocument.objects.create(
        #     order=order,
        #     template=receipt_template
        # )
        #send_mail(agreement)
        #send_mail(receipt)
        return order


class Order(models.Model):
    customer = models.ForeignKey(CustomerData, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent = models.BooleanField(default=False)

    objects = OrderManager()

    @property
    def order_number(self) -> str:
        return f"{self.id:06}/{self.created_at.year}"


class DocumentTypeChoices(models.TextChoices):
    AGREEMENT = "agreement"
    RECEIPT = "receipt"


class DocumentTemplate(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="documents")
    doc_type = models.CharField(max_length=255, choices=DocumentTypeChoices.choices)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


class OrderDocument(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="documents")
    template = models.ForeignKey(DocumentTemplate, on_delete=models.CASCADE)
    sent = models.BooleanField(default=False)

    def get_document_context(self):
        _context = {
            "order": self.order,
            "customer": self.order.customer,
            "products": self.order.products.all(),
        }
        return Context(_context)

    @property
    def document(self):
        with open(self.template.file.path, "rb") as f:
            content = f.read()
        template = Template(content)
        context = self.get_document_context()
        content = template.render(context)
        return pdfkit.from_string(content, False)
