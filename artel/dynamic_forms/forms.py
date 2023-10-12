from collections.abc import Mapping
from typing import Any
from django import forms
from django.forms.utils import ErrorList


class DynamicForm(forms.Form):

    FIELD_TYPE_MAPPING = {
        "singleline": forms.CharField(max_length=255, widget=forms.TextInput(attrs={"class": "form-control"})),
        "multiline": forms.CharField(max_length=255, widget=forms.Textarea(attrs={"class": "form-control"})),
        "email": forms.EmailField(max_length=255, widget=forms.EmailInput(attrs={"class": "form-control"})),
        "number": forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"})),
        "url": forms.URLField(max_length=255, widget=forms.URLInput(attrs={"class": "form-control"})),
        "checkbox": forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={"class": "form-control"})),
        "checkboxes": forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple(attrs={"class": "form-control"})),
        "dropdown": forms.ChoiceField(widget=forms.Select(attrs={"class": "form-control"})),
    }

    def __init__(self, field_list, *args, **kwargs) -> None:
        self.page = kwargs.pop("page")
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        for field in field_list:
            self.fields[field.clean_name] = self.FIELD_TYPE_MAPPING[field.field_type]
