from django import forms
from phonenumber_field.formfields import PhoneNumberField
# from phonenumber_field.widgets import PhoneNumberPrefixWidget

from store.models import (
    CustomerData,
)


class CustomerDataForm(forms.ModelForm):
    class Meta:
        model = CustomerData
        fields = [
            "name", "surname", "email", "phone", 
            "street", "city", "zip_code"
        ]

    name = forms.CharField(
        max_length=255, label="Imię", widget=forms.TextInput(attrs={"class": "form-control"})
    )

    surname = forms.CharField(
        max_length=255, label="Nazwisko", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    street = forms.CharField(
        max_length=255, label="Adres", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    city = forms.CharField(
        max_length=255, label="Miasto", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    zip_code = forms.CharField(
        max_length=255, label="Kod pocztowy", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    email = forms.EmailField(
        max_length=255, label="E-mail", widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    phone = PhoneNumberField(
        region="PL", label="Numer telefonu", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    country = forms.ChoiceField(
        choices=(("PL", "Polska"), ), label="Kraj",
        widget=forms.Select(attrs={"class": "form-control"})
    )
