from django.urls import path, include
from .views import upload_video, video_detail, video_list

urlpatterns = [
    path('video/', upload_video, name='upload_video'),
    path('video/<int:pk>/', video_detail, name='video_detail'),
    path('video/list', video_list, name='video_list'),
]