from django import forms


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


class DynamicForm(forms.Form):

    FIELD_TYPE_MAPPING = {
        "singleline": forms.CharField(max_length=50, widget=forms.TextInput(attrs={"class": "form-control"})),
        "multiline": forms.CharField(max_length=255, widget=forms.Textarea(attrs={"class": "form-control"})),
        "email": forms.EmailField(max_length=255, widget=forms.EmailInput(attrs={"class": "form-control"})),
        "number": forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"})),
        "url": forms.URLField(max_length=255, widget=forms.URLInput(attrs={"class": "form-control"})),
        "checkbox": forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={"class": "form-control"})),
        "checkboxes": forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple(attrs={"class": "form-control"})),
        "dropdown": forms.ChoiceField(widget=forms.Select(attrs={"class": "form-control"})),
    }

    def __init__(self, *args, **kwargs) -> None:
        self.page = kwargs.pop("page")
        self.user = kwargs.pop("user")
        field_list = kwargs.pop("field_list")
        file_uploads = kwargs.pop("file_uploads", False)
        super().__init__(*args, **kwargs)
        for field in field_list:
            self.fields[field.clean_name] = self.FIELD_TYPE_MAPPING[field.field_type]
        if file_uploads:
            self.fields["attachments"] = MultipleFileField(
                required=True, widget=MultipleFileInput(
                    attrs={"class": "form-control"}
                )
            )
