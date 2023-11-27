import logging

from typing import Any, Mapping, Optional, Type, Union
from django import forms
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.forms.utils import ErrorList


from setup.models import (
    ComfyConfig, 
    NavbarPosition
)
from store import SHOP_ESSENTIAL_MAIL_TEMPLATES
from mailings.models import MailTemplate


logger = logging.getLogger(__name__)


class SiteConfigurationForm(forms.ModelForm):
    class Meta:
        model = ComfyConfig
        fields = [
            "logo", "navbar_position", "shop_enabled"
        ]
        widgets = {
            "logo": forms.FileInput(attrs={"class": "form-control"}),
            "navbar_position": forms.Select(attrs={"class": "form-control"}),
            "shop_enabled": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
    
    navbar_position = forms.ChoiceField(
        choices=NavbarPosition.choices,
        widget=forms.Select(attrs={"class": "form-control"}),
        initial=NavbarPosition.LEFT.value
    )


class MailTemplatesFileUploadForm(forms.Form):
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for field_name, desc in SHOP_ESSENTIAL_MAIL_TEMPLATES.items():
            label = field_name.replace("_", " ").capitalize()
            self.fields[field_name] = forms.FileField(
                validators=[FileExtensionValidator(allowed_extensions=["html"])],
                help_text=desc, label=label, widget=forms.FileInput(attrs={"class": "form-control"})
            )
    
    def save(self):
        counter = 0
        for filename, file in self.files.items():
            obj, _created = MailTemplate.objects.get_or_create(
                template_name=filename
            )
            obj.template = file
            obj.save()
            if _created:
                counter +=1
        logger.info(f"Created {counter} mail templates")
        return MailTemplate.objects.count() >= len(SHOP_ESSENTIAL_MAIL_TEMPLATES.keys())
