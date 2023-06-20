from django import forms
from phonenumber_field.formfields import PhoneNumberField
# from phonenumber_field.widgets import PhoneNumberPrefixWidget

from store.models import (
    CustomerData,
)

from django.utils.translation import gettext_lazy as _


class CustomerDataForm(forms.ModelForm):
    class Meta:
        model = CustomerData
        fields = [
            "name", "surname", "email", "phone",
            "street", "city", "zip_code"
        ]

    name = forms.CharField(
        max_length=255, label=_("Name"), widget=forms.TextInput(attrs={"class": "form-control"})
    )

    surname = forms.CharField(
        max_length=255, label=_("Surname"), widget=forms.TextInput(attrs={"class": "form-control"})
    )
    street = forms.CharField(
        max_length=255, label=_("Address"), widget=forms.TextInput(attrs={"class": "form-control"})
    )
    city = forms.CharField(
        max_length=255, label=_("City"), widget=forms.TextInput(attrs={"class": "form-control"})
    )
    zip_code = forms.CharField(
        max_length=255, label=_("Zip-code"), widget=forms.TextInput(attrs={"class": "form-control"})
    )
    email = forms.EmailField(
        max_length=255, label=_("E-mail"), widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    phone = PhoneNumberField(
        region="PL", label=_("Phone number"), widget=forms.TextInput(attrs={"class": "form-control"})
    )
    country = forms.ChoiceField(
        choices=(("PL", _("Polska")), ), label=_("Country"),
        widget=forms.Select(attrs={"class": "form-control"})
    )
