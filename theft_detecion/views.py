import os
from django.shortcuts import get_object_or_404
from .models import Video
from django.conf import settings
from .video_processing import process_video
import re
from datetime import datetime, timezone, timedelta
from .s3_utils import list_processed_videos
import logging
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import VideoDetailSerializer, VideoListSerializer, VideoCreateSerializer


logger = logging.getLogger(__name__)

# Helper Functions


def get_kst_time():
    kst = timezone(timedelta(hours=9))  # KST (UTC+9)
    return datetime.now(kst)


def safe_filename(filename):
    return re.sub(r'[\\/:"*?<>|]+', '_', filename)


def process_and_save_video(video_instance):
    try:
        original_video_url = video_instance.original_video.url
        processed_video_name = safe_filename(os.path.splitext(
            os.path.basename(video_instance.original_video.name))[0]) + ".mp4"
        s3_output_name = f'media/videos/processed/{processed_video_name}'

        upload_time = get_kst_time().strftime("%Y-%m-%d %H:%M:%S")

        print(f"Original video URL: {original_video_url}")
        print(f"S3 Output Key: {s3_output_name}")

        abnormal_behavior_detected = process_video(
            original_video_url, s3_output_name, upload_time)

        video_instance.processed_video.name = s3_output_name
        video_instance.abnormal_behavior_detected = abnormal_behavior_detected
        video_instance.save()

        print(
            f"Video instance saved with processed video path: {video_instance.processed_video.name}")

        return True
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        return False

# API Views


@swagger_auto_schema(
    method='get',
    tags=['theft_detection'],
    operation_summary="List all processed videos",
    operation_description="Get a list of all processed video entries",
    responses={200: 'application/json'}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def video_list(request):
    processed_videos = list_processed_videos()
    return Response({'processed_videos': processed_videos}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    tags=['theft_detection'],
    operation_summary="Upload a new video",
    operation_description="Upload a new video and process it",
    request_body=VideoCreateSerializer,
    responses={201: VideoCreateSerializer, 400: 'Bad Request'}
)
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def upload_video(request):
    serializer = VideoCreateSerializer(data=request.data)
    if serializer.is_valid():
        print("Form is valid. Preparing to save video instance.")
        video_instance = serializer.save()

        try:
            if process_and_save_video(video_instance):
                return Response(VideoCreateSerializer(video_instance).data, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "An error occurred while processing the video."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"An error occurred while uploading the video: {e}")
            return Response({"error": f"An error occurred while uploading the video: {e}"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.warning("Form is not valid.")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    tags=['theft_detection'],
    operation_summary="Retrieve video details",
    operation_description="Get details of a specific video entry",
    responses={200: VideoDetailSerializer, 404: 'Not Found'}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def video_detail(request, pk):
    video = get_object_or_404(Video, pk=pk)
    serializer = VideoDetailSerializer(video)
    return Response(serializer.data, status=status.HTTP_200_OK)
