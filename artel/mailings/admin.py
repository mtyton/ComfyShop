from django.forms import fields

from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register
)

from mailings import models


class MailTemplateAdmin(ModelAdmin):
    model = models.MailTemplate
    menu_label = "Mail templates"
    menu_icon = 'mail'
    menu_order = 100
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = (
        "template_name",
    )
    search_fields = (
        "template_name",
    )
    list_filter = (
        "template_name",
    )
    form_fields = (
        "template_name",
        "template",
    )


class OutgoingMailAdmin(ModelAdmin):
    model = models.OutgoingEmail
    menu_label = "Outgoing mails"
    menu_icon = 'mail'
    menu_order = 100
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = (
        "subject",
        "sent",
    )
    search_fields = (
        "subject",
    )
    list_filter = (
        "subject",
        "sender",
        "recipient",
        "template__template_name",
        "sent",
    )
    readonly_fields = (
        "subject",
        "sender",
        "recipient",
        "sent"
    )


class MailingGroup(ModelAdminGroup):
    menu_label = "Mailings"
    menu_icon = 'mail'
    menu_order = 200
    items = (
        MailTemplateAdmin,
        OutgoingMailAdmin
    )


modeladmin_register(MailingGroup)
