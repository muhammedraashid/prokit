# Generated by Django 5.0.6 on 2024-12-04 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("order_management", "0003_order_applied_coupon_order_discount_amount"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="sub_total",
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
            preserve_default=False,
        ),
    ]