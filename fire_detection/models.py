from django.db import models

class Video(models.Model):
    video_file = models.FileField(upload_to='videos/')
    processed_file = models.FileField(upload_to='processed_videos/', null=True, blank=True)
    fire_detected = models.BooleanField(default=False)

    def __str__(self):
        return self.file.name
