from django.forms import fields

from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register
)
from wagtail.admin.forms.models import WagtailAdminModelForm

from store import models


class ProductConfigAdmin(ModelAdmin):
    model = models.ProductConfig
    list_display = ("author__name", "color", "price")
    search_fields = ("author__name", "color", "price")


class ProductTemplateAdmin(ModelAdmin):
    model = models.ProductTemplate
    list_display = ("title", )


class ProductAdminForm(WagtailAdminModelForm):

    template_title = fields.CharField()
    template_code = fields.CharField()
    template_description = fields.CharField()

    class Meta:
        fields = ("template_title", "template_code", "template_description")
        model = models.Product


class ProductAdmin(ModelAdmin):
    model = models.Product
    form = ProductAdminForm


class StoreAdminGroup(ModelAdminGroup):
    menu_label = "Store"
    menu_icon = 'folder-open-inverse'
    menu_order = 200
    items = (ProductConfigAdmin, ProductTemplateAdmin, ProductAdmin)
    

modeladmin_register(StoreAdminGroup)
