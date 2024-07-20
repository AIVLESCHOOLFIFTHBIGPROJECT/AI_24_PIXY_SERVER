# Generated by Django 5.0.6 on 2024-07-20 11:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "fire_detection",
            "0002_remove_video_processed_file_video_processed_video_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="video",
            name="processed_video",
            field=models.FileField(
                blank=True, null=True, upload_to="media/video_fire/processed/"
            ),
        ),
        migrations.AlterField(
            model_name="video",
            name="video_file",
            field=models.FileField(upload_to="media/video_fire/originals/"),
        ),
    ]
