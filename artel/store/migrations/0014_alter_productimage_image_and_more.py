# Generated by Django 4.1.10 on 2023-09-09 16:42

from django.db import migrations
import easy_thumbnails.fields


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0013_producttemplateparam_alter_product_params_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productimage",
            name="image",
            field=easy_thumbnails.fields.ThumbnailerImageField(upload_to=""),
        ),
        migrations.AlterField(
            model_name="producttemplateimage",
            name="image",
            field=easy_thumbnails.fields.ThumbnailerImageField(upload_to=""),
        )
    ]