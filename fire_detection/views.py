from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Video
from .serializers import VideoSerializer
from .detect_fire import detect_fire
from django.conf import settings
import boto3
from botocore.exceptions import ClientError
import tempfile
import os
from django.http import JsonResponse


## 바꾸기 전
# Initialize S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_KEY,
    aws_secret_access_key=settings.AWS_SECRET,
    region_name=settings.AWS_REGION
)

def index(request):
    return render(request, 'detection/index.html')

def upload(request):
    if request.method == 'POST' and request.FILES.get('video_file'):
        video_file = request.FILES['video_file']
        
        # Upload original video to S3 original/ folder
        try:
            original_key = f"original/{video_file.name}"
            s3.upload_fileobj(
                video_file,
                settings.BUCKET_NAME,
                original_key,
                ExtraArgs={'ContentType': video_file.content_type}
            )
            uploaded_file_url = f"https://{settings.BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{original_key}"
            
            # Define output directory in S3 processed/ folder
            output_dir = 'processed'  # S3 processed directory
            
            # Run fire detection model
            fire_detected, processed_video_url = detect_fire(video_path=original_key, output_dir=output_dir)
            
            # Save the video instance to the database
            video_instance = Video(video_file=original_key, processed_file=processed_video_url, fire_detected=fire_detected)
            video_instance.save()
            
            # Save the video instance to the database
            
            return render(request, 'detection/upload.html', {
                'uploaded_file_url': uploaded_file_url,
                'output_url': processed_video_url,
                'fire_detected': fire_detected
            })
            
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            return render(request, 'detection/upload.html', {'error_message': 'Failed to upload file to S3.'})
    
    return render(request, 'detection/upload.html')

def result(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    serializer = VideoSerializer(video)
    return render(request, 'detection/result.html', {'video': serializer.data})


### 로컬 버전
# def upload(request):
#     if request.method == 'POST' and request.FILES.get('video_file'):
#         video_file = request.FILES['video_file'] # 요청정보에서 파일 가져오기
#         fs = FileSystemStorage() # 이미지 파일 저장
        
#         # 원본 비디오 저장
#         filename = fs.save(video_file.name, video_file) # 파일명
#         uploaded_file_url = fs.url(filename) 
        
#         # 결과 파일 저장할 디렉토리 정의
#         output_dir = os.path.join(settings.MEDIA_ROOT, 'processed_videos')
#         os.makedirs(output_dir, exist_ok = True) # 없으면 디렉토리 만들기
        
#         # 화재 감지 모델 돌리기
#         input_video_path = fs.path(filename)
#         fire_detected, output_path = detect_fire(video_path=input_video_path, output_dir=output_dir)
#         # output_url = fs.url(os.path.relpath(output_path, settings.MEDIA_ROOT))
        
#         output_url = settings.MEDIA_URL + 'processed_videos/' + os.path.basename(output_path)
        
#         return render(request, 'detection/upload.html', {
#             'uploaded_file_url': uploaded_file_url,
#             'output_url': output_url,
#             'fire_detected': fire_detected
#         })
    
#     return render(request, 'detection/upload.html')


## 안됨
# def fire_detection_api(request):
#     return JsonResponse({"message": "Welcome to Fire Detection API!"})

# # Initialize S3 client
# s3 = boto3.client(
#     's3',
#     aws_access_key_id=settings.AWS_KEY,
#     aws_secret_access_key=settings.AWS_SECRET,
#     region_name=settings.AWS_REGION
# )

# @swagger_auto_schema(
#     method='post',
#     tags=['fire_detection'],
#     operation_summary="Upload a video file",
#     operation_description="Upload a video file to S3 and process it for fire detection",
#     request_body=VideoSerializer,
#     responses={200: openapi.Schema(
#         type=openapi.TYPE_OBJECT,
#         properties={
#             'id': openapi.Schema(type=openapi.TYPE_INTEGER),
#             'video_file': openapi.Schema(type=openapi.TYPE_STRING),
#             'processed_file': openapi.Schema(type=openapi.TYPE_STRING),
#             'fire_detected': openapi.Schema(type=openapi.TYPE_BOOLEAN),
#         }
#     )}
# )
# @api_view(['POST'])
# @permission_classes([AllowAny])
# @parser_classes([MultiPartParser, FormParser])
# def upload_video(request):
#     if request.method == 'POST' and request.FILES.get('video_file'):
#         video_file = request.FILES['video_file']
        
#         try:
#             # Upload original video to S3
#             original_key = f"original/{video_file.name}"
#             s3.upload_fileobj(
#                 video_file,
#                 settings.BUCKET_NAME,
#                 original_key,
#                 ExtraArgs={'ContentType': video_file.content_type}
#             )
#             uploaded_file_url = f"https://{settings.BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{original_key}"
            
#             # Run fire detection model
#             fire_detected, processed_video_url = detect_fire(video_path=original_key, output_dir='processed')
            
#             # Save video instance to database
#             video_instance = Video(video_file=original_key, processed_file=processed_video_url, fire_detected=fire_detected)
#             video_instance.save()
            
#             # Return response
#             return Response({
#                 'id': video_instance.id,
#                 'video_file': video_instance.video_file.url,
#                 'processed_file': video_instance.processed_file,
#                 'fire_detected': fire_detected
#             }, status=status.HTTP_200_OK)
            
#         except ClientError as e:
#             return Response({'error_message': 'Failed to upload file to S3.'}, status=status.HTTP_400_BAD_REQUEST)
    
#     return Response({'error_message': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)

# @swagger_auto_schema(
#     method='get',
#     tags=['fire_detection'],
#     operation_summary="List all videos",
#     operation_description="Retrieve a list of all uploaded videos",
#     responses={200: VideoSerializer(many=True)}
# )
# @api_view(['GET'])
# @permission_classes([AllowAny])
# def list_videos(request):
#     videos = Video.objects.all()
#     serializer = VideoSerializer(videos, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)

# @swagger_auto_schema(
#     method='get',
#     tags=['fire_detection'],
#     operation_summary="Retrieve video details",
#     operation_description="Get details of a specific video entry",
#     responses={200: VideoSerializer}
# )
# @api_view(['GET'])
# @permission_classes([AllowAny])
# def get_video(request, video_id):
#     video = get_object_or_404(Video, pk=video_id)
#     serializer = VideoSerializer(video)
#     return Response(serializer.data, status=status.HTTP_200_OK)