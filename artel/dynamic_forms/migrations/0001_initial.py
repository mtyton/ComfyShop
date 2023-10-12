# Generated by Django 4.1.11 on 2023-10-12 17:23

import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import wagtail.contrib.forms.models
import wagtail.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("wagtailcore", "0083_workflowcontenttype"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomEmailForm",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                ("intro", wagtail.fields.RichTextField(blank=True)),
                ("thank_you_text", wagtail.fields.RichTextField(blank=True)),
                ("allow_attachments", models.BooleanField(default=False)),
                ("from_address", models.EmailField(blank=True, help_text="Sender email address", max_length=254)),
                ("to_address", models.CharField(help_text="Comma separated list of recipients", max_length=255)),
                ("subject", models.CharField(help_text="Subject of the email with data", max_length=255)),
            ],
            options={
                "abstract": False,
            },
            bases=(wagtail.contrib.forms.models.FormMixin, "wagtailcore.page"),
        ),
        migrations.CreateModel(
            name="EmailFormSubmission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("form_data", models.JSONField(encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ("submit_time", models.DateTimeField(auto_now_add=True, verbose_name="submit time")),
                ("page", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="wagtailcore.page")),
            ],
            options={
                "verbose_name": "form submission",
                "verbose_name_plural": "form submissions",
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="EmailFormField",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sort_order", models.IntegerField(blank=True, editable=False, null=True)),
                (
                    "clean_name",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Safe name of the form field, the label converted to ascii_snake_case",
                        max_length=255,
                        verbose_name="name",
                    ),
                ),
                (
                    "label",
                    models.CharField(help_text="The label of the form field", max_length=255, verbose_name="label"),
                ),
                (
                    "field_type",
                    models.CharField(
                        choices=[
                            ("singleline", "Single line text"),
                            ("multiline", "Multi-line text"),
                            ("email", "Email"),
                            ("number", "Number"),
                            ("url", "URL"),
                            ("checkbox", "Checkbox"),
                            ("checkboxes", "Checkboxes"),
                            ("dropdown", "Drop down"),
                            ("multiselect", "Multiple select"),
                            ("radio", "Radio buttons"),
                            ("date", "Date"),
                            ("datetime", "Date/time"),
                            ("hidden", "Hidden field"),
                        ],
                        max_length=16,
                        verbose_name="field type",
                    ),
                ),
                ("required", models.BooleanField(default=True, verbose_name="required")),
                (
                    "choices",
                    models.TextField(
                        blank=True,
                        help_text="Comma or new line separated list of choices. Only applicable in checkboxes, radio and dropdown.",
                        verbose_name="choices",
                    ),
                ),
                (
                    "default_value",
                    models.TextField(
                        blank=True,
                        help_text="Default value. Comma or new line separated values supported for checkboxes.",
                        verbose_name="default value",
                    ),
                ),
                ("help_text", models.CharField(blank=True, max_length=255, verbose_name="help text")),
                (
                    "form",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="form_fields",
                        to="dynamic_forms.customemailform",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
    ]
