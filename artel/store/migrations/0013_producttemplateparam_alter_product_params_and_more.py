# Generated by Django 4.1.10 on 2023-08-15 10:44

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0012_deliverymethod_order_uuid_product_uuid_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductTemplateParam",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.CharField(max_length=200)),
                (
                    "param_type",
                    models.CharField(choices=[("int", "Int"), ("str", "String"), ("float", "Float")], max_length=200),
                ),
                (
                    "template",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="template_params",
                        to="store.producttemplate",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AlterField(
            model_name="product",
            name="params",
            field=models.ManyToManyField(
                blank=True,
                limit_choices_to=models.Q(("param__template", models.F("product__template"))),
                through="store.ProductParam",
                to="store.productcategoryparamvalue",
            ),
        ),
        migrations.RenameModel(
            old_name="ProductCategoryParamValue",
            new_name="ProductTemplateParamValue",
        ),
        migrations.DeleteModel(
            name="ProductCategoryParam",
        ),
        migrations.AlterField(
            model_name="producttemplateparamvalue",
            name="param",
            field=modelcluster.fields.ParentalKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="param_values",
                to="store.producttemplateparam",
            ),
        ),
    ]