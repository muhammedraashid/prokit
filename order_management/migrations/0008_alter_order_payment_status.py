# Generated by Django 5.0.6 on 2024-12-07 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("order_management", "0007_alter_order_sub_total"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="payment_status",
            field=models.CharField(
                choices=[
                    ("success", "Success"),
                    ("pending", "Pending"),
                    ("refunded", "Refunded"),
                    ("failed", "Failed"),
                ],
                default="pending",
                max_length=100,
            ),
        ),
    ]
