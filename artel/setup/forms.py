from django import forms
from django.conf import settings

from setup.models import (
    ComfyConfig, 
    NavbarPosition
)


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
