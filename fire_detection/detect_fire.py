import torch
import cv2
from ultralytics import YOLO
import os
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from urllib.parse import urlparse
import tempfile
from venv import logger

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
        print(f"Downloading from bucket: {bucket_name}, key: {s3_key}")
        with open(local_path, 'wb') as f:
            s3.download_fileobj(bucket_name, s3_key, f)
    except Exception as e:
        print(f"Error downloading file from S3: {e}")
        raise

def upload_file_to_s3(file_obj, bucket_name, s3_key):
    try:
        # Ensure the file_obj is read as a file-like object
        s3.upload_fileobj(file_obj, bucket_name, s3_key, ExtraArgs={
            'ContentType': 'video/mp4',
            'CacheControl': 'max-age=86400'
        })
        print(f's3_key: {s3_key}, bucket_name: {bucket_name}')
        logger.info(f"Successfully uploaded {s3_key} to {bucket_name}")
        s3_url = f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
        logger.info(f"Uploaded file URL: {s3_url}")
        return s3_url
    except Exception as e:
        logger.error(f"Error uploading file to S3: {e}")
        raise

def upload_file_to_s3_2(file_path, bucket_name, s3_key):
    try:
        with open(file_path, 'rb') as file_obj:
            s3.upload_fileobj(file_obj, bucket_name, s3_key, ExtraArgs={
                'ContentType': 'video/mp4',
                'CacheControl': 'max-age=86400'
            })
        print(f's3_key: {s3_key}, bucket_name: {bucket_name}')
        logger.info(f"Successfully uploaded {s3_key} to {bucket_name}")
        # 파일의 URL을 반환
        s3_url = f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
        print(f"Uploaded file URL: {s3_url}")  # URL을 로그에 출력
        return s3_url
    except Exception as e:
        logger.error(f"Error uploading file to S3: {e}")
        raise


def detect_fire(s3_input_url, s3_output_name, upload_time):
    model = YOLO('./fire_detection/fire_yolov8n_v2.pt')
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as input_tmp_file:
        local_input_path = input_tmp_file.name
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as output_tmp_file:
        local_output_path = output_tmp_file.name
    
    try:
        # S3에서 original 비디오 다운로드
        download_file_from_s3(settings.BUCKET_NAME, s3_input_url, local_input_path)
        cap = cv2.VideoCapture(local_input_path)
        # 비디오 속성 추출
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        out = cv2.VideoWriter(local_output_path, fourcc, fps, (width, height))
        
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
        
        upload_file_to_s3_2(local_output_path, settings.BUCKET_NAME, s3_output_name)
        
        # processed_key = f'processed/{s3_output_name}'
        # s3.upload_file(s3_output_name, settings.BUCKET_NAME, processed_key) # 여기 수정햇음
        # processed_video_url = f"https://{settings.BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/processed/{s3_output_name}"
        
    except ClientError as e:
        print(f"Error uploading file to S3: {e}")
        return False, ""
        
    finally:
        os.remove(local_input_path)
        os.remove(local_output_path)

    return fire_detected


# def detect_fire(s3_input_url, s3_output_name, upload_time):
#     model = YOLO('./fire_detection/fire_yolov8n_v2.pt')
    
#     try:
#         # Download original video from S3
#         temp_video_path = os.path.join(tempfile.gettempdir(), os.path.basename(video_path))
#         s3.download_file(settings.BUCKET_NAME, video_path, temp_video_path)
#         cap = cv2.VideoCapture(temp_video_path)
#     except ClientError as e:
#         print(f"Error downloading file from S3: {e}")
#         return False, ""

#     # Check if video opened successfully
#     if not cap.isOpened():
#         print(f"Error: Could not open video {video_path}")
#         return False, ""

#     # Video properties
#     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#     fps = cap.get(cv2.CAP_PROP_FPS)

#     # Define output filename and path
#     output_filename = os.path.splitext(os.path.basename(video_path))[0] + '_detected.mp4'
#     output_path = os.path.join(tempfile.gettempdir(), output_filename)

#     # Define VideoWriter for output video
#     fourcc = cv2.VideoWriter_fourcc(*'avc1')
#     out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

#     # Variables for fire detection
#     cons_frame_count = 0
#     fire_detected = False

#     # Process each frame
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break

#         # Run detection model on the frame
#         results = model(frame)

#         # Check each result for fire detection
#         for result in results:
#             if result.boxes is not None:
#                 for box in result.boxes:
#                     class_id = int(box.cls)
#                     class_name = model.names[class_id]
#                     if class_name == 'fire':
#                         cons_frame_count += 1
#                         if cons_frame_count >= 5:
#                             fire_detected = True
#                     else:
#                         cons_frame_count = 0

#             # Draw bounding box on the frame
#             annotated_frame = results[0].plot()
#             out.write(annotated_frame)

#     # Release resources
#     cap.release()
#     out.release()

#     # Upload processed video to S3
#     try:
#         processed_key = f'processed/{output_filename}'
#         s3.upload_file(output_path, settings.BUCKET_NAME, processed_key) # 여기 수정햇음
#         processed_video_url = f"https://{settings.BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/processed/{output_filename}"
#     except ClientError as e:
#         print(f"Error uploading file to S3: {e}")
#         return False, ""

#     return fire_detected, processed_video_url