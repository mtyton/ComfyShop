import pdfkit
import datetime
import builtins
import uuid

from decimal import Decimal
from typing import (
    Any,
    Iterator
)
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
from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed

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
from num2words import num2words

from mailings.models import (
    OutgoingEmail,
    Attachment
)


class BaseImageModel(models.Model):
    image = models.ImageField()
    is_main = models.BooleanField(default=False)

    class Meta:
        abstract = True


class PersonalData(models.Model):

    class Meta:
        abstract = True

    name = models.CharField(max_length=255, blank=True)
    surname = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = PhoneNumberField(blank=True)
    street = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    zip_code = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=120, blank=True)

    @property
    def full_name(self):
        return f"{self.name} {self.surname}"
    
    @property
    def full_address(self):
        return f"{self.street}, {self.zip_code} {self.city}, {self.country}"


class ProductAuthor(PersonalData):
    display_name = models.CharField(max_length=255, unique=True, blank=True)

    def __str__(self):
        return self.display_name


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
    
    panels = [
        FieldPanel("category"),
        FieldPanel("key"),
        FieldPanel("param_type"),
        InlinePanel("param_values")
    ]

    def get_available_values(self) -> Iterator[any]:
        for elem in self.param_values.all():
            yield elem.get_value()


class ProductCategoryParamValue(ClusterableModel):
    param = ParentalKey(ProductCategoryParam, on_delete=models.CASCADE, related_name="param_values")
    value = models.CharField(max_length=255)
    
    def get_value(self):
        try:
            func = getattr(builtins, self.param.param_type)
            return func(self.value)
        except ValueError:
            return

    def __str__(self):
        return f"{self.param.key}: {self.value}"


class ProductTemplate(ClusterableModel):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    author = models.ForeignKey(ProductAuthor, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    tags = TaggableManager()
    
    def __str__(self):
        return self.title

    @property
    def main_image(self):
        try:
            return self.template_images.get(is_main=True)
        except ProductImage.DoesNotExist:
            return self.template_images.first()

    panels = [
        FieldPanel("category"),
        FieldPanel("author"),
        FieldPanel('title'),
        FieldPanel('code'),
        FieldPanel('description'),
        InlinePanel("template_images", label="Template Images"),
        FieldPanel("tags"),
    ]


class ProductTemplateImage(BaseImageModel):
    template = ParentalKey(
        ProductTemplate, on_delete=models.CASCADE, related_name="template_images"
    )
    image = models.ImageField()
    is_main = models.BooleanField(default=False)


class ProductManager(models.Manager):
    
    def get_or_create_by_params(self, params: list[ProductCategoryParamValue], template: ProductTemplate):
        products = self.filter(template=template)

        for param in params:
            products = products.filter(params__pk=param.pk)
            
        # There should be only one
        if not products.count() <= 1:
            raise ValidationError("There should be only one product with given set of params")
        
        product = products.first()
        if not product:
            product = self.create(
                name=f"{template.title} - AUTOGENERATED",
                template=template,
                price=0,
                available=False
            )
            for param in params:
                product.params.add(param)
                
        return product


class Product(ClusterableModel):
    name = models.CharField(max_length=255, blank=True)
    template = models.ForeignKey(ProductTemplate, on_delete=models.CASCADE, related_name="products")
    params = models.ManyToManyField(
        ProductCategoryParamValue, blank=True, through="ProductParam"
    )
    price = models.FloatField()
    available = models.BooleanField(default=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    
    objects = ProductManager()

    panels = [
        FieldPanel("template"),
        FieldPanel("price"),
        FieldPanel("params"),
        FieldPanel("available"),
        FieldPanel("name"),
        InlinePanel("product_images", label="Variant Images"),
    ]

    @property
    def main_image(self):
        try:
            return self.product_images.get(is_main=True)
        except ProductImage.DoesNotExist:
            if main_image := self.template.main_image:
                return main_image
            return self.product_images.first()


    @property
    def tags(self):
        return self.template.tags.all()

    @property
    def author(self):
        return self.template.author

    @property
    def description(self):
        return self.info or self.template.description

    @property
    def title(self):
        return self.name or self.template.title


class ProductImage(BaseImageModel):
    product = ParentalKey(
        "Product", on_delete=models.CASCADE, related_name="product_images"
    )


class ProductParam(models.Model):
    product = ParentalKey(Product, on_delete=models.CASCADE, related_name="product_params")
    param_value = models.ForeignKey(ProductCategoryParamValue, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


# SIGNALS
def validate_param(sender, **kwargs):
    action = kwargs.pop("action")
    if action != "pre_add":
        return
    pk_set = kwargs.get("pk_set")
    product_instance = kwargs.get("instance")
    errors = []
    for pk in pk_set:
        try:
            param = ProductCategoryParamValue.objects.get(pk=pk).param
        except ProductCategoryParamValue.DoesNotExist:
            # TODO log this
            ...
        count = product_instance.params.filter(productparam__param_value__param=param).count()
        if count >= 1:
            errors.append(ValueError("Product param with this key already exists."))
    
    if errors:
        raise ValidationError(errors)
    

m2m_changed.connect(validate_param, Product.params.through)


class ProductListPage(Page):
    # TODO add filters

    description = wagtail_fields.RichTextField(blank=True)
    tags = TaggableManager(blank=True)

    def _get_items(self):
        if self.tags.all():
            return ProductTemplate.objects.filter(tags__in=self.tags.all())
        return ProductTemplate.objects.all()
    
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


class OrderProductManager(models.Manager):
    def create_from_cart(self, items: dict[str, Product|int], order: models.Model):
        pks = []
        for item in items:
            if item["quantity"] < 1:
                # TODO - logging
                continue
            
            pk = self.create(
                product=item["product"],
                order=order,
                quantity=item["quantity"]
            ).pk
            pks.append(pk)
        return self.filter(pk__in=pks)


class OrderProduct(models.Model):   
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="products")
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    objects = OrderProductManager()


class OrderManager(models.Manager):

    def _get_order_number(self, author: ProductAuthor):
        number_of_prev_orders = OrderProduct.objects.filter(
            product__template__author=author
        ).values("order").distinct().count()
        number_of_prev_orders += 1
        year = datetime.datetime.now().year
        return f"{author.id}/{number_of_prev_orders:06}/{year}"

    def _send_notifications(
            self, order: models.Model, author: ProductAuthor, 
            customer_data: dict[str, Any], docs: list[models.Model]
        ):
        # for user
        attachments = [
            Attachment(
                content=doc.generate_document({"customer_data": customer_data}), 
                contenttype="application/pdf", 
                name=f"{doc.template.doc_type}_{order.order_number}.pdf"
            ) for doc in docs
        ]
        mail_subject = f"Wygenerowano umowę numer {order.order_number} z dnia {order.created_at.strftime('%d.%m.%Y')}"
        user_mail = OutgoingEmail.objects.send(
            recipient=customer_data["email"],
            subject=mail_subject,
            context = {
                "docs": docs,
                "order_number": order.order_number,
                "customer_email": customer_data["email"],
            }, sender=settings.DEFAULT_FROM_EMAIL,
            template_name="order_created_user",
            attachments=attachments
        )
        # for author
        author_mail = OutgoingEmail.objects.send(
            recipient=author.email,
            subject=mail_subject,
            context = {
                "docs": docs,
                "order_number": order.order_number,
                "manufacturer_email": author.email,
            }, sender=settings.DEFAULT_FROM_EMAIL,
            template_name="order_created_author",
            attachments=attachments
        )
        return user_mail is not None and author_mail is not None

    def create_from_cart(
            self, cart_items: list[dict[str, str|dict]], 
            payment_method: models.Model| None, 
            customer_data: dict[str, Any]
        ) -> models.QuerySet:
        # split cart
        orders_pks = []

        payment_method = payment_method or PaymentMethod.objects.first()
        doc_templates = DocumentTemplate.objects.filter(
            doc_type__in=[DocumentTypeChoices.AGREEMENT, DocumentTypeChoices.RECEIPT]
        )

        for item in cart_items:
            author = item["author"]
            author_products = item["products"]
            
            order = self.create(
                payment_method=payment_method, 
                order_number=self._get_order_number(author)
            )
            OrderProduct.objects.create_from_cart(author_products, order)
            orders_pks.append(order.pk)
            docs = []
            for template in doc_templates:
                doc = OrderDocument.objects.create(
                    order=order, template=template
                )
                docs.append(doc)
            sent = self._send_notifications(order, author, customer_data, docs)
            
            if not sent:
                # TODO - store data temporarily
                raise Exception("Error while sending emails")

        return Order.objects.filter(pk__in=orders_pks)


class PaymentMethod(models.Model):
    name = models.CharField(max_length=255)

    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)


class Order(models.Model):
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent = models.BooleanField(default=False)
    order_number = models.CharField(max_length=255, null=True)
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    objects = OrderManager()

    @property
    def manufacturer(self) -> str:
        return self.products.first().product.author

    @property
    def total_price(self) -> Decimal:
        return sum(
            [order_product.product.price * order_product.quantity 
             for order_product in self.products.all()]
        )

    @property
    def total_price_words(self) -> str:
        return num2words(self.total_price, lang="pl", to="currency", currency="PLN")

    @property
    def payment_date(self) -> datetime.date:
        return self.created_at.date() + datetime.timedelta(days=7)


class DocumentTypeChoices(models.TextChoices):
    AGREEMENT = "agreement"
    RECEIPT = "receipt"


class DocumentTemplate(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="documents")
    # there may be only one document of each type
    doc_type = models.CharField(max_length=255, choices=DocumentTypeChoices.choices, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


class OrderDocument(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="documents")
    template = models.ForeignKey(DocumentTemplate, on_delete=models.CASCADE)

    def get_document_context(self):
        _context = {
            "order": self.order,
            "author": self.order.manufacturer,
            "order_products": self.order.products.all(),
            "payment_data": self.order.payment_method,
        }
        return Context(_context)

    def generate_document(self, extra_context: dict = None):
        extra_context = extra_context or {}
        context = self.get_document_context()
        context.update(extra_context)

        with open(self.template.file.path, "r", encoding="utf-8") as f:
            content = f.read()
        template = Template(content)
        content = template.render(context)
        return pdfkit.from_string(content, False)
