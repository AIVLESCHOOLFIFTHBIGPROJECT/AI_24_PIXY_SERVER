from django.db import models
from django.utils import timezone


class Video(models.Model):
    video_file = models.FileField(upload_to='originals/')
    processed_video = models.FileField(upload_to='processed/', null=True, blank=True)
    fire_detected = models.BooleanField(default=False)
    store_id = models.IntegerField(default = 1)
    upload_time = models.DateTimeField(default=timezone.now) # default 값 추가

    def __str__(self):
        return self.video_file.name