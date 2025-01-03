# Generated by Django 5.0.6 on 2024-12-03 09:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("coupon", "0004_remove_coupon_discount_type"),
        ("products", "0025_variant_is_listed_alter_product_is_listed"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Cart",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "discount_amount",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "applied_coupon",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="coupon.coupon",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cart",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CartItems",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("price_at_time", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "cart",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cartitems",
                        to="cart.cart",
                    ),
                ),
                (
                    "variant_size",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cart_items",
                        to="products.variantsize",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="cartitems",
            constraint=models.UniqueConstraint(
                fields=("cart", "variant_size"), name="unique_cart_variant"
            ),
        ),
    ]
