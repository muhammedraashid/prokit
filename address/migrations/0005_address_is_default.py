# Generated by Django 5.0.6 on 2024-11-14 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("address", "0004_address_city_address_country_address_state"),
    ]

    operations = [
        migrations.AddField(
            model_name="address",
            name="is_default",
            field=models.BooleanField(default=False),
        ),
    ]
