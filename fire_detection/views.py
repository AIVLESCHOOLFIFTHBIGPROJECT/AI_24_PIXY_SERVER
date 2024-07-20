import os
import re
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view, permission_classes, parser_classes
from urllib.parse import urlparse, urlunparse
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Video
from .serializers import VideoDetailSerializer, VideoListSerializer, VideoCreateSerializer
from .detect_fire import detect_fire, upload_file_to_s3
from django.conf import settings
import logging
from datetime import datetime, timezone, timedelta
from .s3_utils import list_processed_videos

logger = logging.getLogger(__name__)


def get_kst_time():
    kst = timezone(timedelta(hours=9))  # KST (UTC+9)
    return datetime.now(kst)


def safe_filename(filename):
    return re.sub(r'[\\/:"*?<>|]+', '_', filename)


def transform_s3_url(url):
    parsed_url = urlparse(url)
    return urlunparse((parsed_url.scheme, settings.AWS_S3_CUSTOM_DOMAIN, parsed_url.path, parsed_url.params, parsed_url.query, parsed_url.fragment))


def process_and_save_video(video_instance):
    try:

        original_video_url = video_instance.video_file.url  # 원본 영상 URL
        processed_video_name = safe_filename(os.path.splitext(
            os.path.basename(video_instance.video_file.name))[0]) + ".mp4"
        s3_output_name = f'media/videos_fire/processed/{processed_video_name}'
        orgin_s3_output_name = f'videos_fire/processed/{processed_video_name}'

        upload_time = get_kst_time().strftime("%Y-%m-%d %H:%M:%S")

        print(f"Original video URL: {original_video_url} - DEBUG300")
        print(f"S3 Output Key: {s3_output_name} - DEBUG301")

        # 화재 감지 여부
        fire_detected = detect_fire(
            original_video_url, s3_output_name, upload_time)

        # print(f"Original video URL(transformed): {transform_video_url} - DEBUG301")
        # print(f"S3 Output Key: {s3_output_name}")

        # fire_detected = detect_fire(transform_video_url, s3_output_name, upload_time)

        # 비디오 모델 저장
        video_instance.processed_video.name = orgin_s3_output_name
        video_instance.fire_detected = fire_detected
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
    tags=['fire_detection'],
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
    tags=['fire_detection'],
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

        original_filename = safe_filename(request.FILES['video_file'].name)
        s3_key = f'media/videos_fire/original/{original_filename}'
        orign_s3_key = f'videos_fire/original/{original_filename}'

        try:
            print(f"Attempting to upload file to S3 with key {s3_key}")
            s3_url = upload_file_to_s3(
                request.FILES['video_file'], settings.AWS_STORAGE_BUCKET_NAME, s3_key)

            print(f"File uploaded to S3 successfully: {s3_key}")
            print(f"Uploaded file URL: {s3_url}")

            video_instance.video_file.name = orign_s3_key
            video_instance.save()

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
    tags=['fire_detection'],
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
    # return render(request, 'video_processor/video_detail.html', {'video': video, 'transformed_video_url': video.processed_video.url})
