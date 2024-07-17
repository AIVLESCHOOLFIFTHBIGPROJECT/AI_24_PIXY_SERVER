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

def index(request):
    return render(request, 'detection/index.html')

def upload(request):
    if request.method == 'POST' and request.FILES.get('video_file'):
        video_file = request.FILES['video_file'] # 요청정보에서 파일 가져오기
        fs = FileSystemStorage() # 이미지 파일 저장
        # 원본 비디오 저장
        filename = fs.save(video_file.name, video_file) # 파일명
        uploaded_file_url = fs.url(filename) 
        
        # 결과 파일 저장할 디렉토리 정의
        output_dir = os.path.join(settings.MEDIA_ROOT, 'processed_videos')
        os.makedirs(output_dir, exist_ok = True) # 없으면 디렉토리 만들기
        
        # 화재 감지 모델 돌리기
        input_video_path = fs.path(filename)
        fire_detected, output_path = detect_fire(video_path=input_video_path, output_dir=output_dir)
        output_url = fs.url(os.path.relpath(output_path, settings.MEDIA_ROOT))
        
        return render(request, 'detection/upload.html', {
            'uploaded_file_url': uploaded_file_url,
            'output_url': output_url,
            'fire_detected': fire_detected
        })
    
    return render(request, 'detection/upload.html')

def result(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    return render(request, 'detection/result.html', {'video': video})
