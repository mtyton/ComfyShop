from django.test import TestCase

from dynamic_forms.models import (
    CustomEmailForm,
    EmailFormField
)


class CustomEmailFormTestCase(TestCase):
    def setUp(self):
        self.form = CustomEmailForm.objects.create(
            from_address="comfy-test@egalitare.pl",
            to_address="comfy-dest@egalitare.pl",
            subject="Test Form", allow_attachments=False
        )
        EmailFormField.objects.create(
            label="Name",
            field_type="singleline",
            required=True,
            form=self.form
        )
        EmailFormField.objects.create(
            label="Message",
            field_type="multiline",
            required=True,
            form=self.form
        )
        EmailFormField.objects.create(
            label="Email",
            field_type="email",
            required=True,
            form=self.form
        )
        EmailFormField.objects.create(
            label="Number",
            field_type="number",
            required=True,
            form=self.form
        )
        EmailFormField.objects.create(
            label="URL",
            field_type="url",
            required=True,
            form=self.form
        )
        EmailFormField.objects.create(
            label="Checkbox",
            field_type="checkbox",
            required=True,
            form=self.form
        )
        EmailFormField.objects.create(
            label="Checkboxes",
            field_type="checkboxes",
            required=True,
            choices="a,b,c",
            form=self.form
        )
        EmailFormField.objects.create(
            label="Dropdown",
            field_type="dropdown",
            required=True,
            choices="a,b,c",
            form=self.form
        )
        EmailFormField.objects.create(
            label="MultiSelect",
            field_type="multiselect",
            required=True,
            choices="a,b,c",
            form=self.form
        )
        EmailFormField.objects.create(
            label="Radio",
            field_type="radio",
            required=True,
            choices="a,b,c",
            form=self.form
        )
        EmailFormField.objects.create(
            label="Date",
            field_type="date",
            required=True,
            form=self.form
        )
        EmailFormField.objects.create(
            label="DateTime",
            field_type="datetime",
            required=True,
            form=self.form
        )
        EmailFormField.objects.create(
            label="Hidden",
            field_type="hidden",
            required=True,
            form=self.form
        )


    def test_create_form_submission_without_files(self):
        ...
