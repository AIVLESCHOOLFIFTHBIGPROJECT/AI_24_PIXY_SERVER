# Generated by Django 5.0.6 on 2024-07-20 15:16

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("fire_detection", "0003_alter_video_processed_video_alter_video_video_file"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="video",
            name="video_file",
        ),
        migrations.AddField(
            model_name="video",
            name="original_video",
            field=models.FileField(
                default=django.utils.timezone.now,
                upload_to="media/videos_fire/originals/",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="video",
            name="processed_video",
            field=models.FileField(
                blank=True, null=True, upload_to="media/videos_fire/processed/"
            ),
        ),
    ]