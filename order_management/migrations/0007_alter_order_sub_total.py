# Generated by Django 5.0.6 on 2024-12-07 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("order_management", "0006_alter_order_discount_amount"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="sub_total",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]