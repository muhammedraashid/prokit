# Generated by Django 5.0.6 on 2024-11-22 04:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0023_variantsize_is_listed"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="variantsize",
            name="is_listed",
        ),
        migrations.AlterField(
            model_name="product",
            name="is_listed",
            field=models.BooleanField(blank=True, default=True),
        ),
    ]
