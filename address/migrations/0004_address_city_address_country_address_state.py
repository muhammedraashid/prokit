# Generated by Django 5.0.6 on 2024-11-14 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("address", "0003_address_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="address",
            name="city",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="address",
            name="country",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="address",
            name="state",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
