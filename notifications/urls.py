from django.urls import path
from .views import notification_list, mark_as_read, send_notification, send_notification_to_all

urlpatterns = [
    path('', notification_list, name='notification_list'),
    path('read/<int:notification_id>/', mark_as_read, name='mark_as_read'),
    path('send/', send_notification, name='send_notification'),
    path('send-to-all/', send_notification_to_all, name='send_notification_to_all'),
]
