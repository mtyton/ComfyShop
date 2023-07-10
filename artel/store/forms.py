from django import forms
from phonenumber_field.formfields import PhoneNumberField

from store.models import (
    ProductCategoryParamValue,
    ProductCategoryParam,
    ProductCategory
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


class ProductCategoryParamForm(forms.ModelForm):
    class Meta:
        model = ProductCategoryParam
        fields = ("key", "value")
        readonly_fields = ("key", )

    def __init__(self, instance, *args, **kwargs):
        super().__init__(*args, instance=instance, **kwargs)
        self.fields["key"].widget.attrs["disabled"] = True
        self.fields["value"].choices = [
            (param_value.pk, param_value.value) for param_value in instance.param_values.all()
        ]

    value = forms.ModelChoiceField(
        queryset=ProductCategoryParamValue.objects.none(),
        widget=forms.RadioSelect(attrs={"class": "form-control"})
    )

    def save(self, *args, **kwargs):
        return ProductCategoryParamValue.objects.get(
            param=self.instance,
            value=str(self.cleaned_data["value"])
        )
