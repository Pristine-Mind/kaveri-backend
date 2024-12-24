# Generated by Django 4.2.17 on 2024-12-22 00:38

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="description",
            field=tinymce.models.HTMLField(help_text="A detailed description of the product.", verbose_name="Description"),
        ),
    ]
