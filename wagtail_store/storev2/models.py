from django.db import models
from rest_framework.pagination import LimitOffsetPagination
from taggit.managers import TaggableManager
from wagtail import fields as wagtail_fields
from wagtail.models import Page

from store_api.models import Product


class PaginationMixin:
    def get_paginator(self):
        return LimitOffsetPagination()

    def paginate(self, queryset):
        paginator = self.get_paginator()
        return paginator.paginate_queryset(queryset, self.request)


class StorePage(Page):
    store = models.OneToOneField("store_api.Store", on_delete=models.CASCADE, related_name="page")
    description = wagtail_fields.RichTextField(blank=True)
    tags = TaggableManager(blank=True)

    def get_context(self, request):
        context = super().get_context(request)
        # FIXME getting all products may cause website to crash
        # context["products"] = Product.objects.filter(store=self.store)
        context["groups"] = self.store.product_groups.all()
        return context


class AllProductsListPage(PaginationMixin, Page):
    store = models.OneToOneField("store_api.Store", on_delete=models.CASCADE, related_name="all_products_list")

    def get_context(self, request):
        context = super().get_context(request)
        context["products"] = self.paginate(Product.objects.filter(store=self.store))
        return context


class GroupListPage(PaginationMixin, Page):
    store = models.ForeignKey("store_api.Store", on_delete=models.CASCADE, related_name="product_lists")
    group = models.OneToOneField("store_api.ProductGroup", on_delete=models.CASCADE, related_name="page")
