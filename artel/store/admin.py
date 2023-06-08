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
    model = models.ProductTemplate
    list_display = ("title", "code")


class ProductAdmin(ModelAdmin):
    model = models.Product
    list_display = ("title", "price")



class DocumentTemplateAdmin(ModelAdmin):
    model = models.DocumentTemplate
    list_display = ("name", "doc_type")


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
        DocumentTemplateAdmin
    )


modeladmin_register(StoreAdminGroup)
