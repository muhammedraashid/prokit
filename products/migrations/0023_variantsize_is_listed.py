# Generated by Django 5.0.6 on 2024-11-22 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0022_remove_variant_stock"),
    ]

    operations = [
        migrations.AddField(
            model_name="variantsize",
            name="is_listed",
            field=models.BooleanField(blank=True, default=True),
        ),
    ]