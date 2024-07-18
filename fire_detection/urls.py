from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.upload_video, name='upload_video'),
    path('video/<int:pk>/', views.video_detail, name='video_detail'),
    path('video/list', views.list_processed_videos, name='video_list'),
] 