from django.forms import fields

from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register
)
from wagtail.admin.forms.models import WagtailAdminModelForm

from store import models


class ProductAuthorAdmin(ModelAdmin):
    model = models.ProductAuthor
    list_display = ("name", )


class ProductCategoryAdmin(ModelAdmin):
    model = models.ProductCategory
    list_display = ("name", )


class ProductCategoryParamAdmin(ModelAdmin):
    model = models.ProductCategoryParam
    list_display = ("key", "param_type")


class ProductTemplateAdmin(ModelAdmin):
    menu_label = "Product design"
    model = models.ProductTemplate
    list_display = ("title", "code")


class ProductAdmin(ModelAdmin):
    menu_label = "Product variant"
    model = models.Product
    list_display = ("title", "price")


class PaymentMethodAdmin(ModelAdmin):
    model = models.PaymentMethod
    list_display = ("name", "active")


class DocumentTemplateAdmin(ModelAdmin):
    model = models.DocumentTemplate
    list_display = ("name", )


class StoreAdminGroup(ModelAdminGroup):
    menu_label = "Store"
    menu_icon = 'folder-open-inverse'
    menu_order = 200
    items = (
        ProductAuthorAdmin, 
        ProductCategoryAdmin, 
        ProductCategoryParamAdmin,
        ProductTemplateAdmin,
        ProductAdmin,
        DocumentTemplateAdmin,
        PaymentMethodAdmin
    )


modeladmin_register(StoreAdminGroup)
