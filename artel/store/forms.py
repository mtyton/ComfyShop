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


class ProductCategoryParamFormset(forms.BaseModelFormSet):
    ...


class ProductCategoryParamValueForm(forms.ModelForm):
    class Meta:
        model = ProductCategoryParamValue
        fields = ("key", "value")
    
    key = forms.CharField(required=True)
    value = forms.ModelChoiceField(
        queryset=ProductCategoryParamValue.objects.none(),
        widget=forms.RadioSelect(attrs={"class": "btn-check", "type": "radio", "autocomplete": "off"}),
        required=True
    )

    def _get_instace(self, key: str):
        return ProductCategoryParam.objects.get(key=key)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        key = self.initial.get("key")
        if not key:
            return
        self.cat_param = self._get_instace(key)
        self.fields["value"].choices = [
            (param_value.pk, param_value.value) for param_value in self.cat_param.param_values.all()
        ]

    def save(self, *args, **kwargs):
        param_value = ProductCategoryParamValue.objects.get(
            param__key=str(self.cleaned_data["key"]),
            value=str(self.cleaned_data["value"])
        )
        print(param_value or "DUPSKo")
        return param_value
