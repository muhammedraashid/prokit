# Generated by Django 5.0.6 on 2024-12-03 10:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cart", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="cart",
            name="applied_coupon",
        ),
        migrations.RemoveField(
            model_name="cart",
            name="discount_amount",
        ),
    ]