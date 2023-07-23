# Generated by Django 4.1.9 on 2023-07-22 17:18

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0011_productparam_delete_templateparamvalue_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeliveryMethod",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("price", models.FloatField(default=0)),
                ("active", models.BooleanField(default=True)),
            ],
        ),
        migrations.AddField(
            model_name="order",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AddField(
            model_name="product",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AddField(
            model_name="order",
            name="delivery_method",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to="store.deliverymethod"),
        ),
    ]
