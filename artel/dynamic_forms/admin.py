from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register
)

from dynamic_forms import models

class CustomEmailFormAdmin(ModelAdmin):
    model = models.CustomEmailForm
    menu_label = "Email Forms"
    menu_icon = 'mail'
    menu_order = 100
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = (
        "title",
        "slug",
    )
    search_fields = (
        "title",
        "slug",
    )
    list_filter = (
        "title",
        "slug",
    )
    form_fields = (
        "slug",
        "intro",
        "thank_you_text",
        "from_address",
        "to_address",
        "subject",
    )

class CustomFormGroup(ModelAdminGroup):
    menu_label = "Custom Forms"
    menu_icon = 'tasks'
    menu_order = 100
    items = (
        CustomEmailFormAdmin,
    )

modeladmin_register(CustomFormGroup)
