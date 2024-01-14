from django.db import models
from wagtail.models import Page
from wagtail import fields as wagtail_fields
from taggit.managers import TaggableManager

from store_api.models import Product

# Create your models here.


class StorePage(Page):
    store = models.OneToOneField("store_api.Store", on_delete=models.CASCADE, related_name="page")
    description = wagtail_fields.RichTextField(blank=True)
    tags = TaggableManager(blank=True)


class AllProductsListPage(Page):
    store = models.OneToOneField("store_api.Store", on_delete=models.CASCADE, related_name="all_products_list")
    
    def get_context(self, request):
        context = super().get_context(request)
        context["items"] = Product.objects.filter(store=self.store)
        return context


class GroupListPage(Page):
    store = models.ForeignKey("store_api.Store", on_delete=models.CASCADE, related_name="product_lists")
    group = models.OneToOneField("store_api.ProductGroup", on_delete=models.CASCADE, related_name="page")
