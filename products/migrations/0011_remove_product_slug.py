# Generated by Django 5.0.6 on 2024-11-12 17:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0010_product_slug"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="slug",
        ),
    ]
