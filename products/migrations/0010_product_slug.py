# Generated by Django 5.0.6 on 2024-11-12 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0009_remove_product_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="slug",
            field=models.SlugField(blank=True),
        ),
    ]
