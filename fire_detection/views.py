from django.shortcuts import render, redirect, get_object_or_404
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from .forms import VideoForm
from .models import Video
from django.core.files.storage import default_storage
from .detect_fire import detect_fire
import os
from django.conf import settings
from django.core.exceptions import ValidationError

import boto3
from botocore.exceptions import ClientError
import re
from urllib.parse import urlparse, urlunparse
import dotenv

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

### S3 연결
def index(request):
    return render(request, 'detection/index.html')

# Load environment variables
dotenv.load_dotenv('./.env')
AWS_KEY = os.environ.get('AWS_KEY')
AWS_SECRET = os.environ.get('AWS_SECRET')
AWS_REGION = os.environ.get('AWS_REGION')
BUCKET_NAME = os.environ.get('AWS_NAME')

# Initialize S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_KEY,
    aws_secret_access_key=AWS_SECRET,
    region_name=AWS_REGION
)

def upload(request):
    if request.method == 'POST' and request.FILES.get('video_file'):
        video_file = request.FILES['video_file']
        
        # Upload original video to S3 original/ folder
        try:
            original_key = f"original/{video_file.name}"
            s3.upload_fileobj(
                video_file,
                bucket_name,
                original_key,
                ExtraArgs={'ACL': 'public-read'}
            )
            uploaded_file_url = f"https://{bucket_name}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{original_key}"
            
            # Define output directory in S3 processed/ folder
            processed_key = f"processed/{video_file.name.replace('.', '_')}_detected.mp4"
            output_url = f"https://{bucket_name}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{processed_key}"
            
            # Run fire detection model
            fire_detected, output_path = detect_fire(video_path=original_key, output_dir=processed_key)
            
            return render(request, 'detection/upload.html', {
                'uploaded_file_url': uploaded_file_url,
                'output_url': output_url,
                'fire_detected': fire_detected
            })
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            return render(request, 'detection/upload.html', {'error_message': 'Failed to upload file to S3.'})
    
    return render(request, 'detection/upload.html')

def result(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    return render(request, 'detection/result.html', {'video': video})

