# Generated by Django 5.0.6 on 2024-12-27 09:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0006_address_address_type_alter_address_name'),
        ('order_management', '0013_alter_order_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='address',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='address.address'),
        ),
    ]
