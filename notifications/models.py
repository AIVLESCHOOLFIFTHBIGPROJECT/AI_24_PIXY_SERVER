from django.db import models
from django.conf import settings

class Notification(models.Model):
    SENDER_CHOICES = [
        ('admin', 'Admin'),
        ('system', 'System'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    sender_type = models.CharField(max_length=10, choices=SENDER_CHOICES)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')

    def __str__(self):
        return self.message
