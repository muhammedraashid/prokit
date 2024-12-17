# Generated by Django 5.0.6 on 2024-12-11 07:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cart", "0003_cart_applied_coupon_cart_discount_amount"),
        ("coupon", "0004_remove_coupon_discount_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cart",
            name="applied_coupon",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="coupon.coupon",
            ),
        ),
        migrations.AlterField(
            model_name="cart",
            name="discount_amount",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]