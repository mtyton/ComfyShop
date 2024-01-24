from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from easy_thumbnails.signals import saved_file
from phonenumber_field.modelfields import PhoneNumberField
from wagtail.models import Page

from wagtail_store.tasks import generate_thumbnails


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


class StoreUser(PersonalData, models.Model):
    auth_user = models.OneToOneField(User, on_delete=models.CASCADE)


class StoreMembership(models.Model):
    store = models.ForeignKey("Store", on_delete=models.CASCADE)
    user = models.ForeignKey("StoreUser", on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)


class Store(models.Model):
    owner = models.ForeignKey(StoreUser, on_delete=models.CASCADE)
    members = models.ManyToManyField(StoreUser, related_name="stores", blank=True, through=StoreMembership)


class ProductGroup(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)


# Products
class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    group = models.ForeignKey(ProductGroup, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products", blank=True)


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")

    name = models.CharField(max_length=255, blank=True)
    sku = models.CharField(max_length=255, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    config = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name


@receiver(saved_file)
def generate_thumbnails_async(sender, fieldfile, **kwargs):
    generate_thumbnails.delay(model=sender, pk=fieldfile.instance.pk, field=fieldfile.field.name)
