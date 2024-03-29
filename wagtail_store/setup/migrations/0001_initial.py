# Generated by Django 4.1.10 on 2023-08-17 20:21

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ComfyConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("logo", models.ImageField(upload_to="images")),
                (
                    "navbar_position",
                    models.CharField(
                        choices=[("top", "Top"), ("left", "Left"), ("right", "Right")], default="top", max_length=20
                    ),
                ),
                ("shop_enabled", models.BooleanField(default=False)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
