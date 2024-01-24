from django import forms
from django.db.models import Model
from django.utils.translation import gettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber

from store.models import (
    DeliveryMethod,
    PaymentMethod,
    Product,
    ProductTemplate,
    ProductTemplateParamValue,
)


class CustomerDataForm(forms.Form):
    name = forms.CharField(max_length=255, label=_("Name"), widget=forms.TextInput(attrs={"class": "form-control"}))

    surname = forms.CharField(
        max_length=255, label=_("Surname"), widget=forms.TextInput(attrs={"class": "form-control"})
    )
    street = forms.CharField(
        max_length=255, label=_("Address"), widget=forms.TextInput(attrs={"class": "form-control"})
    )
    city = forms.CharField(max_length=255, label=_("City"), widget=forms.TextInput(attrs={"class": "form-control"}))
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
        choices=(("PL", _("Polska")),), label=_("Country"), widget=forms.Select(attrs={"class": "form-control"})
    )
    payment_method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.filter(active=True),
        label="Sposób płatności",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    delivery_method = forms.ModelChoiceField(
        queryset=DeliveryMethod.objects.filter(active=True),
        label="Sposób dostawy",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def serialize(self):
        """Clean method should return JSON serializable"""
        new_cleaned_data = {}
        for key, value in self.cleaned_data.items():
            if isinstance(value, PhoneNumber):
                new_cleaned_data[key] = str(value)
            elif isinstance(value, Model):
                new_cleaned_data[key] = value.pk
            else:
                new_cleaned_data[key] = value
        return new_cleaned_data


class ButtonToggleSelect(forms.RadioSelect):
    template_name = "store/forms/button_toggle_select.html"


class ProductTemplateConfigForm(forms.Form):
    def _create_dynamic_fields(self, template: ProductTemplate):
        template_params = template.template_params.all()
        for param in template_params:
            queryset = ProductTemplateParamValue.objects.filter(param=param)
            if queryset.count() >= 4:
                widget = forms.Select(attrs={"class": "form-select"})
            else:
                widget = ButtonToggleSelect(attrs={"class": "btn-group btn-group-toggle"})
            self.fields[param.key] = forms.ModelChoiceField(
                queryset=queryset,
                widget=widget,
            )

    def __init__(self, template: ProductTemplate, *args, **kwargs):
        self.template = template
        super().__init__(*args, **kwargs)
        self._create_dynamic_fields(template)

    def get_product(self):
        params = list(self.cleaned_data.values())
        return Product.objects.get_or_create_by_params(template=self.template, params=params)
