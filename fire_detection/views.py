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
from .serializers import VideoSerializer
from .detect_fire import detect_fire, upload_file_to_s3
from django.conf import settings
import logging
from datetime import datetime, timezone, timedelta
import os
import re
from .s3_utils import list_processed_videos




logger = logging.getLogger(__name__)

def get_kst_time():
    kst = timezone(timedelta(hours=9))  # KST (UTC+9)
    return datetime.now(kst)

def safe_filename(filename):
    return re.sub(r'[\\/:"*?<>|]+', '_', filename)

def transform_s3_url(url):
    parsed_url = urlparse(url)
    correct_path = parsed_url.path.replace('/media/videos/processed/', '/videos/processed/')
    return urlunparse((parsed_url.scheme, parsed_url.netloc, correct_path, parsed_url.params, parsed_url.query, parsed_url.fragment))

def transform_original_video_url(url):
    parsed_url = urlparse(url)
    correct_path = parsed_url.path.replace(
        '/media/videos/original/', '/videos/original/')
    return urlunparse((parsed_url.scheme, parsed_url.netloc, correct_path, parsed_url.params, parsed_url.query, parsed_url.fragment))

def process_and_save_video(video_instance):
    try:
        original_video_url = video_instance.video_file.url  # Use video_file instead of original_video
        processed_video_name = safe_filename(os.path.splitext(
            os.path.basename(video_instance.video_file.name))[0]) + ".mp4"
        s3_output_name = f'videos/processed/{processed_video_name}'
        upload_time = get_kst_time().strftime("%Y-%m-%d %H:%M:%S")

        print(f"Original video URL: {original_video_url} - DEBUG300")
        print(f"S3 Output Key: {s3_output_name}")
        
        transform_video_url = transform_original_video_url(original_video_url)

        print(f"Original video URL(transformed): {transform_video_url} - DEBUG301")
        # print(f"S3 Output Key: {s3_output_name}")
        
        fire_detected = detect_fire(transform_video_url, s3_output_name, upload_time)

        video_instance.processed_video.name = s3_output_name
        video_instance.fire_detected = fire_detected
        video_instance.save()

        print(f"Video instance saved with processed video path: {video_instance.processed_video.name}")

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
    responses={200: VideoSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def video_list(request):
    processed_videos = list_processed_videos()
    return render(request, 'fire_detection/video_list.html', {'processed_videos': processed_videos})


@swagger_auto_schema(
    method='post',
    tags=['fire_detection'],
    operation_summary="Upload a new video",
    operation_description="Upload a new video and process it",
    request_body=VideoSerializer,
    responses={201: VideoSerializer, 400: 'Bad Request'}
)
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def upload_video(request):
    if request.method == 'POST':
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            print("Form is valid. Preparing to save video instance.")
            video_instance = serializer.save()

            original_filename = safe_filename(request.FILES['video_file'].name)
            s3_key = f'media/videos_fire/original/{original_filename}'
            orign_s3_key = f'videos_fire/original/{original_filename}'
            try:
                print(f"Attempting to upload file to S3 with key {s3_key}")
                
                # Use the file object directly from the request.FILES
                file_obj = request.FILES['video_file']
                
                s3_url = upload_file_to_s3(file_obj, settings.BUCKET_NAME, s3_key)

                print(f"File uploaded to S3 successfully: {s3_key}")
                print(f"Uploaded file URL: {s3_url}")

                video_instance.video_file.name = orign_s3_key
                video_instance.save()

                if process_and_save_video(video_instance):
                    return redirect('video_detail', pk=video_instance.pk)
                else:
                    return Response({"error": "An error occurred while processing the video."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"An error occurred while uploading the video: {e}")
                return Response({"error": f"An error occurred while uploading the video: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.warning("Form is not valid.")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return render(request, 'fire_detection/upload_video.html')


@swagger_auto_schema(
    method='get',
    tags=['fire_detection'],
    operation_summary="Retrieve video details",
    operation_description="Get details of a specific video entry",
    responses={200: VideoSerializer, 404: 'Not Found'}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def video_detail(request, pk):
    video = get_object_or_404(Video, pk=pk)
    transformed_video_url = transform_s3_url(video.processed_video.url)
    
    print(f"S3 processed transformed URL : {transformed_video_url}" + "-DEBUG302")
    return render(request, 'fire_detection/video_detail.html', {'video': video, 'transformed_video_url': transformed_video_url})


# def upload(request):
#     if request.method == 'POST' and request.FILES.get('video_file'):
#         video_file = request.FILES['video_file']
        
#         # Upload original video to S3 original/ folder
#         try:
#             original_key = f"original/{video_file.name}"
#             s3.upload_fileobj(
#                 video_file,
#                 settings.BUCKET_NAME,
#                 original_key,
#                 ExtraArgs={'ContentType': video_file.content_type}
#             )
#             uploaded_file_url = f"https://{settings.BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{original_key}"
            
#             # Define output directory in S3 processed/ folder
#             output_dir = 'processed'  # S3 processed directory
            
#             # Run fire detection model
#             fire_detected, processed_video_url = detect_fire(video_path=original_key, output_dir=output_dir)
            
#             # Save the video instance to the database
#             video_instance = Video(video_file=original_key, processed_file=processed_video_url, fire_detected=fire_detected)
#             video_instance.save()
            
#             # Save the video instance to the database
            
#             return render(request, 'detection/upload.html', {
#                 'uploaded_file_url': uploaded_file_url,
#                 'output_url': processed_video_url,
#                 'fire_detected': fire_detected
#             })
            
#         except ClientError as e:
#             print(f"Error uploading file to S3: {e}")
#             return render(request, 'detection/upload.html', {'error_message': 'Failed to upload file to S3.'})
    
#     return render(request, 'detection/upload.html')

def result(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    serializer = VideoSerializer(video)
    return render(request, 'detection/result.html', {'video': serializer.data})
