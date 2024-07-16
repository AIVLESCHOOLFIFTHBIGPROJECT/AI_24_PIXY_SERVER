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

# def upload(request):
#     if request.method == 'POST':
#         form = VideoForm(request.POST, request.FILES)
#         if form.is_valid():
#             video = form.save()  # Save the form instance to create a Video object
#             try:
#                 # Process the video for fire detection
#                 fire_detected = detect_fire(video_path=video.video_file.path, output_path='output.mp4')
#                 return render(request, 'detection/upload.html', {
#                     'uploaded_file_url': video.video_file.url,
#                     'fire_detected': fire_detected
#                 })
#             except ValidationError as e:
#                 form.add_error(None, e)
#         else:
#             # Handle form validation errors
#             print(form.errors)
#     else:
#         form = VideoForm()
#     return render(request, 'detection/upload.html', {'form': form})

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

    #     # 출력 비디오 저장
    #     video = Video(video_file=filename, 
    #                   processed_file=f'processed_videos/{os.path.basename(input_video_path)}_detected.mp4', 
    #                   fire_detected = fire_detected)
    #     video.save()

    #     return redirect('result', video_id=video.id)
    
    # return render(request, 'detection/upload.html')

# def upload(request):
#     if request.method == 'POST' and request.FILES.get('video_file'):
#         video_file = request.FILES['video_file']
#         fs = FileSystemStorage()
#         filename = fs.save(video_file.name, video_file)

#         # Rename the uploaded video file
#         input_video_path = fs.path(filename)
#         input_video_name, input_video_ext = os.path.splitext(filename)
#         renamed_filename = f"{input_video_name}_result{input_video_ext}"
#         renamed_path = os.path.join(os.path.dirname(input_video_path), renamed_filename)
#         os.rename(input_video_path, renamed_path)

#         uploaded_file_url = fs.url(renamed_filename)

#         # Process the video for fire detection
#         output_folder = os.path.join(fs.location, 'output_videos')
#         os.makedirs(output_folder, exist_ok=True)  # Create output folder if not exists
#         output_path = os.path.join(output_folder, 'output.mp4')
#         fire_detected = detect_fire(video_path=renamed_path, output_path=output_path)
#         output_url = fs.url(os.path.relpath(output_path, fs.location))

#         return render(request, 'detection/upload.html', {
#             'uploaded_file_url': uploaded_file_url,
#             'output_url': output_url,
#             'fire_detected': fire_detected
#         })
#     return render(request, 'detection/upload.html')


def result(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    return render(request, 'detection/result.html', {'video': video})
