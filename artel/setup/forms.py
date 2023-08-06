from django import forms
from django.conf import settings
from colorfield.fields import ColorField
import os


class SiteConfigurationForm(forms.Form):
    logo = forms.ImageField(required=False)
    shop_enabled = forms.BooleanField(required=False)
    navbar_position = forms.ChoiceField(
        choices=[
            ('left', 'Left'),
            ('right', 'Right'),
            ('top', 'Top'),
        ],
        initial='left',
        widget=forms.RadioSelect
    )
    skin = forms.ChoiceField(
        choices=[
            ('light', 'Light'),
            ('dark', 'Dark'),
            ('custom', 'Custom'),
        ],
        widget=forms.Select
    )

    def save_logo(self):
        if self.cleaned_data['logo']:
            logo = self.cleaned_data['logo']
            filename = os.path.join(settings.MEDIA_ROOT, 'images/icons', logo.name)
            with open(filename, 'wb') as f:
                for chunk in logo.chunks():
                    f.write(chunk)
            return os.path.join('images/icons', logo.name)
        return None


class SkinChangerForm(forms.Form):
    COLOR_PALETTE = [
        ("#FFFFFF", "white", ),
        ("#000000", "black", ),
    ]

    background_color = ColorField(samples=COLOR_PALETTE)
    font_color = ColorField(samples=COLOR_PALETTE)
    hr_color = ColorField(samples=COLOR_PALETTE)
    link_color = ColorField(samples=COLOR_PALETTE)
    hover_on_link_color = ColorField(samples=COLOR_PALETTE)
