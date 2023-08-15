from django import forms
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from django.db.models import Model

from store.models import (
    ProductTemplate,
    ProductTemplateParam,
    Product,
    PaymentMethod,
    DeliveryMethod
)




class CustomerDataForm(forms.Form):

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
    payment_method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.filter(active=True), label="Sposób płatności",
        widget=forms.Select(attrs={"class": "form-control"})
    )
    delivery_method = forms.ModelChoiceField(
        queryset=DeliveryMethod.objects.filter(active=True), label="Sposób dostawy",
        widget=forms.Select(attrs={"class": "form-control"})
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
        category_params = template.category.category_params.all()
        for param in category_params:
            self.fields[param.key] = forms.ModelChoiceField(
                queryset=ProductTemplateParam.objects.filter(param=param),
                widget=ButtonToggleSelect(attrs={"class": "btn-group btn-group-toggle"}),
            )
    
    def __init__(
            self, template: ProductTemplate, *args, **kwargs
        ):
        self.template = template
        super().__init__(*args, **kwargs)
        self._create_dynamic_fields(template)

    def get_product(self):
        params = list(self.cleaned_data.values())
        return Product.objects.get_or_create_by_params(template=self.template, params=params)
