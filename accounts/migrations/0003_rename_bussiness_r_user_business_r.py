# Generated by Django 4.2 on 2024-07-07 05:12

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_user_is_agreement1_user_is_agreement2_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="user",
            old_name="bussiness_r",
            new_name="business_r",
        ),
    ]