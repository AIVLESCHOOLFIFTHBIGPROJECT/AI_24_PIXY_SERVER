# Generated by Django 5.0.6 on 2024-07-12 01:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="storeupload",
            name="uploaded_file",
            field=models.FileField(null=True, upload_to="store/"),
        ),
    ]