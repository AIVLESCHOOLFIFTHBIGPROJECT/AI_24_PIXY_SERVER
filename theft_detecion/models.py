# video_processor/models.py
from django.db import models
from django.utils import timezone


class Video(models.Model):
    original_video = models.FileField(upload_to='media/videos/originals/')
    processed_video = models.FileField(
        upload_to='media/videos/processed/', blank=True, null=True)
    abnormal_behavior_detected = models.BooleanField(default=False)
    store_id = models.IntegerField(default=1)
    upload_time = models.DateTimeField(default=timezone.now)  # default 값을 추가

    def __str__(self):
        return self.original_video.name
