from django import forms

from dynamic_forms.widgets import CheckboxInput, CheckboxSelectMultiple, RadioSelect


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class HoneypotField(forms.BooleanField):
    default_widget = forms.HiddenInput({"style": "display:none !important;", "tabindex": "-1", "autocomplete": "off"})

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", HoneypotField.default_widget)
        kwargs["required"] = False
        super().__init__(*args, **kwargs)

    def clean(self, value):
        if cleaned_value := super().clean(value):
            raise forms.ValidationError("")
        else:
            return cleaned_value


class DynamicForm(forms.Form):
    FIELD_TYPE_MAPPING = {
        "singleline": forms.CharField(max_length=50, widget=forms.TextInput(attrs={"class": "form-control"})),
        "multiline": forms.CharField(max_length=255, widget=forms.Textarea(attrs={"class": "form-control"})),
        "email": forms.EmailField(max_length=255, widget=forms.EmailInput(attrs={"class": "form-control"})),
        "number": forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"})),
        "url": forms.URLField(max_length=255, widget=forms.URLInput(attrs={"class": "form-control"})),
        "checkbox": forms.BooleanField(required=False, widget=CheckboxInput(attrs={"class": "form-check"})),
        "checkboxes": forms.MultipleChoiceField(
            required=False, widget=CheckboxSelectMultiple(attrs={"class": "form-check"})
        ),
        "dropdown": forms.ChoiceField(widget=forms.Select(attrs={"class": "form-control"})),
        "multiselect": forms.MultipleChoiceField(widget=forms.SelectMultiple(attrs={"class": "form-control"})),
        "radio": forms.ChoiceField(widget=RadioSelect(attrs={"class": "form-control"})),
        "date": forms.DateField(widget=forms.DateInput(attrs={"class": "form-control"})),
        "datetime": forms.DateTimeField(widget=forms.DateTimeInput(attrs={"class": "form-control"})),
        "hidden": forms.CharField(widget=forms.HiddenInput()),
    }

    def __init__(self, *args, **kwargs) -> None:
        kwargs.pop("page", "")
        kwargs.pop("user", "")
        field_list = kwargs.pop("field_list")
        file_uploads = kwargs.pop("file_uploads", False)
        super().__init__(*args, **kwargs)
        for field in field_list:
            f = self.FIELD_TYPE_MAPPING[field.field_type]
            f.label = field.label
            if hasattr(f, "choices"):
                f.choices = [(v, v) for v in field.choices.split(",")]
            f.required = field.required
            f.help_text = field.help_text or ""
            self.fields[field.clean_name] = f
        if file_uploads:
            self.fields["attachments"] = MultipleFileField(
                required=True, widget=MultipleFileInput(attrs={"class": "form-control"})
            )
        # add honeypot field
        self.fields["secret_honey"] = HoneypotField()

    def clean(self):
        cleaned_data = super().clean()
        new_cleaned_data = {}
        for key, value in cleaned_data.items():
            if isinstance(value, list):
                if isinstance(self.fields[key], MultipleFileField):
                    continue

                cleaned_data[key] = ",".join(value)
            if key == "secret_honey":
                continue

            new_cleaned_data[key] = value

        return new_cleaned_data
