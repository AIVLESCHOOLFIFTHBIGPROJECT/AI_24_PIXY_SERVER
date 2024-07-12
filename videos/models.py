from django.db import models
from store.models import Store

class Video(models.Model):
    title = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    
    original_video = models.URLField(blank=True, null=True)
    fire_classified_video = models.URLField(blank=True, null=True)
    theft_classified_video = models.URLField(blank=True, null=True)
    
    is_fire_detected = models.BooleanField(default=False)
    is_theft_detected = models.BooleanField(default=False)


    def __str__(self):
        return self.title