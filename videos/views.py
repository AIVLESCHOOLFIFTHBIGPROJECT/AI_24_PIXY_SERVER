# videos/views.py

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .forms import VideoForm
from .models import Video, Store
from django.conf import settings
import boto3
import os
import json

@api_view(['POST'])
def upload_video(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    form = VideoForm(request.POST, request.FILES)
    if form.is_valid():
        video = form.save(commit=False)
        video.store = store

        # S3에 원본 비디오 업로드
        original_video_url = upload_to_s3(request.FILES['original_video'])
        video.original_video = original_video_url
        video.save()

        # Lambda 함수 호출
        invoke_lambda_function(video.id, original_video_url)

        return Response({"message": "Video uploaded and processing started"}, status=status.HTTP_201_CREATED)
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

def upload_to_s3(file):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    file_name = os.path.join('videos/originals/', file.name)
    s3_client.upload_fileobj(
        file,
        settings.AWS_STORAGE_BUCKET_NAME,
        file_name,
        ExtraArgs={
            "ContentType": file.content_type
        }
    )
    return f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_name}"

def invoke_lambda_function(video_id, video_url):
    lambda_client = boto3.client('lambda', region_name=settings.AWS_S3_REGION_NAME)
    payload = {
        "video_id": video_id,
        "video_url": video_url
    }
    response = lambda_client.invoke(
        FunctionName='your_lambda_function_name',
        InvocationType='Event',  # 비동기 호출
        Payload=json.dumps(payload)
    )
    return response

@api_view(['POST'])
def lambda_callback(request):
    video_id = request.data.get('video_id')
    fire_classified_video_url = request.data.get('fire_classified_video_url')
    theft_classified_video_url = request.data.get('theft_classified_video_url')
    is_fire_detected = request.data.get('is_fire_detected')
    is_theft_detected = request.data.get('is_theft_detected')

    video = get_object_or_404(Video, id=video_id)
    video.fire_classified_video = fire_classified_video_url
    video.theft_classified_video = theft_classified_video_url
    video.is_fire_detected = is_fire_detected
    video.is_theft_detected = is_theft_detected
    video.save()

    return Response({'status': 'success'}, status=status.HTTP_200_OK)
