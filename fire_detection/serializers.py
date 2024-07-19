from rest_framework import serializers
from .models import Video


class VideoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'


class VideoDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['processed_video', 'fire_detected',
                  'store_id', 'upload_time']


class VideoListSerializer(serializers.ModelSerializer):
    processed_video = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['processed_video']

    def get_processed_video(self, obj):
        processed_videos = self.context.get('processed_videos', [])
        for url in processed_videos:
            if url.split('/')[-1] == obj.processed_video.name:
                return url
        return None