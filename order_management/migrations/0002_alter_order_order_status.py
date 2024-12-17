# Generated by Django 5.0.6 on 2024-12-04 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("order_management", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="order_status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("processing", "Processing"),
                    ("shipped", "Shipped"),
                    ("delivered", "Delivered"),
                    ("cancelled", "Cancelled"),
                    ("return_requested", "Requested To Return"),
                    ("returned", "Returned"),
                ],
                default="pending",
                max_length=100,
            ),
        ),
    ]