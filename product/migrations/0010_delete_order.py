# Generated by Django 5.0.6 on 2024-07-16 04:36

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("product", "0009_product_stock_sales_stock_alter_product_sales_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Order",
        ),
    ]
