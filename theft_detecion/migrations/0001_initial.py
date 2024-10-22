# Generated by Django 5.0.6 on 2024-07-17 06:17

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Video",
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
                ("original_video", models.FileField(upload_to="videos/originals/")),
                (
                    "processed_video",
                    models.FileField(
                        blank=True, null=True, upload_to="videos/processed/"
                    ),
                ),
                ("abnormal_behavior_detected", models.BooleanField(default=False)),
                ("store_id", models.IntegerField(default=1)),
                (
                    "upload_time",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
            ],
        ),
    ]
