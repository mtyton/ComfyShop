from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from wagtail.tests.utils import WagtailPageTests

from dynamic_forms.forms import DynamicForm
from dynamic_forms.models import CustomEmailForm, EmailFormField


class CustomEmailFormTestCase(WagtailPageTests):
    def setUp(self):
        self.form = CustomEmailForm.objects.create(
            slug="test",
            title="Test Form",
            path="test",
            depth=0,
            numchild=0,
            live=True,
            has_unpublished_changes=False,
            from_address="comfy-test@egalitare.pl",
            to_address="comfy-dest@egalitare.pl",
            subject="Test Form",
            allow_attachments=False,
        )
        EmailFormField.objects.create(label="Name", field_type="singleline", required=True, form=self.form)
        EmailFormField.objects.create(label="Message", field_type="multiline", required=True, form=self.form)
        EmailFormField.objects.create(label="Email", field_type="email", required=True, form=self.form)
        EmailFormField.objects.create(label="Number", field_type="number", required=True, form=self.form)
        EmailFormField.objects.create(label="URL", field_type="url", required=True, form=self.form)
        EmailFormField.objects.create(label="Checkbox", field_type="checkbox", required=True, form=self.form)
        EmailFormField.objects.create(
            label="Checkboxes", field_type="checkboxes", required=True, choices="a,b,c", form=self.form
        )
        EmailFormField.objects.create(
            label="Dropdown", field_type="dropdown", required=True, choices="a,b,c", form=self.form
        )
        EmailFormField.objects.create(
            label="MultiSelect", field_type="multiselect", required=True, choices="a,b,c", form=self.form
        )
        EmailFormField.objects.create(label="Radio", field_type="radio", required=True, choices="a,b,c", form=self.form)
        EmailFormField.objects.create(label="Date", field_type="date", required=True, form=self.form)
        EmailFormField.objects.create(label="DateTime", field_type="datetime", required=True, form=self.form)
        EmailFormField.objects.create(label="Hidden", field_type="hidden", required=True, form=self.form)

    def test_generate_html_form_from_model(self):
        html_form = self.form.get_form()
        self.assertIsInstance(html_form, DynamicForm)
        self.assertEqual(len(html_form.fields), 14)
        self.assertEqual(html_form.fields["name"].label, "Name")
        self.assertEqual(html_form.fields["name"].required, True)
        self.assertEqual(html_form.fields["name"].widget.attrs["class"], "form-control")
        self.assertIsInstance(html_form.fields["name"], forms.CharField)
        self.assertIsInstance(html_form.fields["message"], forms.CharField)
        self.assertIsInstance(html_form.fields["email"].widget, forms.EmailInput)
        self.assertIsInstance(html_form.fields["number"].widget, forms.NumberInput)

    def test_create_form_submission_success_without_files(self):
        form_data = {
            # generate data for this class self.form.get_form()
            "name": "Test",
            "message": "Test message",
            "email": "test@test.com",
            "number": 1,
            "url": "http://example.com",
            "checkbox": True,
            "checkboxes": ["a", "b"],
            "dropdown": "a",
            "multiselect": ["a", "b"],
            "radio": "a",
            "date": "2020-01-01",
            "datetime": "2020-01-01 00:00:00",
            "hidden": "hidden",
        }
        form = self.form.get_form(form_data)
        self.assertTrue(form.is_valid())
        # change field not to be required
        field = EmailFormField.objects.get(label="Name", form=self.form)
        field.required = False
        field.save()
        form = self.form.get_form(form_data)
        self.assertTrue(form.is_valid())
        # it should also work without this field
        form_data.pop("name")
        form = self.form.get_form(form_data)
        self.assertTrue(form.is_valid())

    def test_create_form_submission_success_with_files(self):
        self.form.allow_attachments = True
        self.form.save()
        form_data = {
            # generate data for this class self.form.get_form()
            "name": "Test",
            "message": "Test message",
            "email": "test@test.com",
            "number": 1,
            "url": "http://example.com",
            "checkbox": True,
            "checkboxes": ["a", "b"],
            "dropdown": "a",
            "multiselect": ["a", "b"],
            "radio": "a",
            "date": "2020-01-01",
            "datetime": "2020-01-01 00:00:00",
            "hidden": "hidden",
        }
        files = {
            "attachments": [SimpleUploadedFile("test.txt", b"test")],
        }
        form = self.form.get_form(form_data, files=files)
        self.assertTrue(form.is_valid())

    def test_create_form_submission_failure_without_files_missing_data(self):
        form_data = {
            # generate data for this class self.form.get_form()
            "message": "Test message",
            "email": "test@test.com",
            "number": 1,
            "url": "http://example.com",
            "checkbox": True,
            "checkboxes": ["a", "b"],
            "dropdown": "a",
            "multiselect": ["a", "b"],
            "radio": "a",
            "date": "2020-01-01",
            "datetime": "2020-01-01 00:00:00",
            "hidden": "hidden",
        }
        form = self.form.get_form(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors["name"], ["This field is required."])

        form_data.pop("url")
        form = self.form.get_form(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)
        self.assertEqual(form.errors["name"], ["This field is required."])
        self.assertEqual(form.errors["url"], ["This field is required."])
        # make Field not required
        field = EmailFormField.objects.get(label="Hidden", form=self.form)
        field.required = False
        field.save()
        # it should also work without this field
        form_data.pop("hidden")
        form = self.form.get_form(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)
        self.assertEqual(form.errors["name"], ["This field is required."])
        self.assertEqual(form.errors["url"], ["This field is required."])

    def test_create_form_submission_failure_with_files_missing_data(self):
        self.form.allow_attachments = True
        self.form.save()
        form_data = {
            # generate data for this class self.form.get_form()
            "message": "Test message",
            "email": "test@test.com",
            "number": 1,
            "url": "http://example.com",
            "checkbox": True,
            "checkboxes": ["a", "b"],
            "dropdown": "a",
            "multiselect": ["a", "b"],
            "radio": "a",
            "date": "2020-01-01",
            "datetime": "2020-01-01 00:00:00",
            "hidden": "hidden",
        }
        files = {
            "attachments": [SimpleUploadedFile("test.txt", b"test")],
        }
        form = self.form.get_form(form_data, files=files)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors["name"], ["This field is required."])

        form_data.pop("url")
        form = self.form.get_form(form_data, files=files)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)
        self.assertEqual(form.errors["name"], ["This field is required."])
        self.assertEqual(form.errors["url"], ["This field is required."])
        # make Field not required
        field = EmailFormField.objects.get(label="Hidden", form=self.form)
        field.required = False
        field.save()
        # it should also work without this field
        form_data.pop("hidden")
        form = self.form.get_form(form_data, files=files)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)
        self.assertEqual(form.errors["name"], ["This field is required."])
        self.assertEqual(form.errors["url"], ["This field is required."])
        # Now try without files
        form = self.form.get_form(form_data, files={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)
        self.assertEqual(form.errors["name"], ["This field is required."])
        self.assertEqual(form.errors["url"], ["This field is required."])
        self.assertEqual(form.errors["attachments"], ["This field is required."])

    def test_no_hidden_field_in_clean_data_success(self):
        form_data = {
            # generate data for this class self.form.get_form()
            "name": "Test",
            "message": "Test message",
            "email": "test@test.com",
            "number": 1,
            "url": "http://example.com",
            "checkbox": True,
            "checkboxes": ["a", "b"],
            "dropdown": "a",
            "multiselect": ["a", "b"],
            "radio": "a",
            "date": "2020-01-01",
            "datetime": "2020-01-01 00:00:00",
            "hidden": "hidden",
        }
        form = self.form.get_form(form_data)
        self.assertTrue(form.is_valid())
        cleaned_data = form.cleaned_data
        self.assertIn("hidden", cleaned_data)
        self.assertNotIn("secret_honey", cleaned_data)
        self.assertIn("hidden", form.fields)
        self.assertIn("secret_honey", form.fields)
