# Generated by Django 5.0.6 on 2024-07-16 12:08

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("product", "0010_delete_order"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="sales",
            name="p_num",
        ),
    ]