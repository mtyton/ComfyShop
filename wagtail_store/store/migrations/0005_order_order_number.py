# Generated by Django 4.1.9 on 2023-06-18 11:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0004_documenttemplate_order_paymentmethod_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="order_number",
            field=models.CharField(max_length=255, null=True),
        ),
    ]
