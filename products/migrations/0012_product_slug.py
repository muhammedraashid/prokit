# Generated by Django 5.0.6 on 2024-11-12 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0011_remove_product_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="slug",
            field=models.SlugField(default=12),
            preserve_default=False,
        ),
    ]