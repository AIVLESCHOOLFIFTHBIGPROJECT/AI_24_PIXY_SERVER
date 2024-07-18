import torch
import cv2
from ultralytics import YOLO
import os
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from urllib.parse import urlparse
import tempfile

# S3 연결하기
s3 = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_KEY,
    aws_secret_access_key=settings.AWS_SECRET,
    region_name=settings.AWS_REGION
)

def download_file_from_s3(bucket_name, s3_url, local_path):
    try:
        parsed_url = urlparse(s3_url)
        s3_key = parsed_url.path.lstrip('/')
        # 디버깅 정보 추가
        print(f"Downloading from bucket: {bucket_name}, key: {s3_key}")
        with open(local_path, 'wb') as f:
            s3.download_fileobj(bucket_name, s3_key, f)
    except Exception as e:
        print(f"Error downloading file from S3: {e}")
        raise
    
def upload_file_to_s3(local_path, bucket_name, s3_key):
    try:
        with open(local_path, 'rb') as f:
            s3.upload_fileobj(f, bucket_name, s3_key, ExtraArgs={
                'ContentType': 'video/mp4',
                'CacheControl': 'max-age=86400'
            })
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        raise

def detect_fire(video_path, output_dir, model_path='./fire_detection/fire_yolov8n_v2.pt'):
    model = YOLO(model_path)

    try:
        # Download original video from S3
        temp_video_path = os.path.join(tempfile.gettempdir(), os.path.basename(video_path))
        s3.download_file(settings.BUCKET_NAME, video_path, temp_video_path)
        cap = cv2.VideoCapture(temp_video_path)
    except ClientError as e:
        print(f"Error downloading file from S3: {e}")
        return False, ""

    # Check if video opened successfully
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return False, ""

    # Video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Define output filename and path
    output_filename = os.path.splitext(os.path.basename(video_path))[0] + '_detected.mp4'
    output_path = os.path.join(tempfile.gettempdir(), output_filename)

    # Define VideoWriter for output video
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Variables for fire detection
    cons_frame_count = 0
    fire_detected = False

    # Process each frame
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Run detection model on the frame
        results = model(frame)

        # Check each result for fire detection
        for result in results:
            if result.boxes is not None:
                for box in result.boxes:
                    class_id = int(box.cls)
                    class_name = model.names[class_id]
                    if class_name == 'fire':
                        cons_frame_count += 1
                        if cons_frame_count >= 5:
                            fire_detected = True
                    else:
                        cons_frame_count = 0

            # Draw bounding box on the frame
            annotated_frame = results[0].plot()
            out.write(annotated_frame)

    # Release resources
    cap.release()
    out.release()

    # Upload processed video to S3
    try:
        processed_key = f'processed/{output_filename}'
        s3.upload_file(output_path, settings.BUCKET_NAME, processed_key) # 여기 수정햇음
        processed_video_url = f"https://{settings.BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/processed/{output_filename}"
    except ClientError as e:
        print(f"Error uploading file to S3: {e}")
        return False, ""

    return fire_detected, processed_video_url

### local 버전
# def detect_fire(video_path, output_dir, model_path='./fire_detection/fire_yolov8n_v2.pt'):
#     model = YOLO(model_path)

#     # cv로 비디오 열기
#     cap = cv2.VideoCapture(video_path)
    
#     # 비디오 열리지 않을 시 에러 메시지 출력
#     if not cap.isOpened():
#         print(f"Error: Could not open video {video_path}")
#         return False

#     # 비디오 속성
#     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) # 영상 너비
#     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) # 영상 높이
#     fps = cap.get(cv2.CAP_PROP_FPS)

#     # 코덱 설정 & 영상 생성 객체 생성
#     fourcc = cv2.VideoWriter_fourcc(*'avc1') # 동영상 파일 코덱 포맷 지정
#     output_filename = os.path.splitext(os.path.basename(video_path))[0] + '_detected.mp4' # 결과 파일 이름 지정
#     output_path = os.path.join(output_dir, output_filename) # 결과파일 들어갈 경로 지정
#     out = cv2.VideoWriter(output_path, fourcc, fps, (width, height)) # VideoWriter 객체 생성

#     # 화재 감지 연속 5번으로 되어야 True 반환하기
#     cons_frame_count = 0 # 화재 감지된 프레임 수 (연속)
#     fire_detected = False

#     # 비디오 열어서 프레임 가져오기
#     while cap.isOpened():
#         # ret: 동영상 열기 성공 여부, frame: 현재 프레임 (np.ndarray)
#         ret, frame = cap.read()
#         # 동영상 못 열었으면 멈추기
#         if not ret:
#             break

#         # 현재 프레임에 대해 모델 run
#         results = model(frame)
        
#         # 각 프레임 감지 결과 확인
#         for result in results:
#             if result.boxes is not None:
#                 for box in result.boxes:
#                     class_id = int(box.cls)
#                     class_name = model.names[class_id]
#                     # 화재 감지 시 화재 감지 카운트 1씩 증가
#                     if class_name == 'fire':
#                         cons_frame_count += 1
#                         if cons_frame_count >= 5:
#                             fire_detected = True
#                     else:
#                         cons_frame_count = 0

#             # 프레임에 bounding box 그리기
#             annotated_frame = results[0].plot()
#             out.write(annotated_frame)
            
#     cap.release()
#     out.release()
    
#     return fire_detected, output_path
