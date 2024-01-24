from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)

from setup.models import ComfyConfig


class ConfigAdmin(ModelAdmin):
    model = ComfyConfig
    list_display = ("updated",)


class SetupModelAdminGroup(ModelAdminGroup):
    menu_label = "Setup"
    menu_icon = "folder-open-inverse"
    menu_order = 200
    items = (ConfigAdmin,)


modeladmin_register(SetupModelAdminGroup)
