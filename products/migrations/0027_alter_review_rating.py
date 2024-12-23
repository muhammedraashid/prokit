# Generated by Django 5.0.6 on 2024-12-19 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0026_variant_created_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="review",
            name="rating",
            field=models.PositiveIntegerField(
                choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]
            ),
        ),
    ]