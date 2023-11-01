from django import forms


class CheckboxInput(forms.CheckboxInput):
    template_name = "widgets/checkbox.html"


class CheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    template_name = "widgets/checkbox_multiple.html"


class RadioSelect(forms.RadioSelect):
    template_name = "widgets/radio_multiple.html"
