import os
from django.shortcuts import get_object_or_404
from .models import Video
from django.conf import settings
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
import boto3

import tempfile
from venv import logger
import cv2

import numpy as np
import mediapipe as mp
from urllib.parse import urlparse
import tensorflow as tf
from ultralytics import YOLO

# 랜덤 시드 고정
np.random.seed(42)
tf.random.set_seed(42)

sts_client = boto3.client(
    'sts',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

assumed_role_object = sts_client.assume_role(
    RoleArn=settings.S3_ROLE_ARN,
    RoleSessionName="AssumeRoleSession"
)

s3_client = boto3.client(
    's3',
    aws_access_key_id=assumed_role_object['Credentials']['AccessKeyId'],
    aws_secret_access_key=assumed_role_object['Credentials']['SecretAccessKey'],
    aws_session_token=assumed_role_object['Credentials']['SessionToken'],
    region_name=settings.AWS_REGION
)

# YOLOv8 모델 로드
model_path_yolo = 'yolov8n.pt'  # YOLOv8 모델 경로
yolo_model = YOLO(model_path_yolo)

# MediaPipe 초기화
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# 제외할 랜드마크 설정
excluded_landmarks = {
    mp_pose.PoseLandmark.NOSE.value,
    mp_pose.PoseLandmark.LEFT_EYE_INNER.value,
    mp_pose.PoseLandmark.LEFT_EYE.value,
    mp_pose.PoseLandmark.LEFT_EYE_OUTER.value,
    mp_pose.PoseLandmark.RIGHT_EYE_INNER.value,
    mp_pose.PoseLandmark.RIGHT_EYE.value,
    mp_pose.PoseLandmark.RIGHT_EYE_OUTER.value,
    mp_pose.PoseLandmark.LEFT_EAR.value,
    mp_pose.PoseLandmark.RIGHT_EAR.value,
    mp_pose.PoseLandmark.MOUTH_LEFT.value,
    mp_pose.PoseLandmark.MOUTH_RIGHT.value
}

# 커스텀 LSTM 레이어 정의


class CustomLSTM(tf.keras.layers.LSTM):
    def __init__(self, *args, **kwargs):
        kwargs.pop('time_major', None)
        super(CustomLSTM, self).__init__(*args, **kwargs)

    @classmethod
    def from_config(cls, config):
        config.pop('time_major', None)
        return cls(**config)

    def get_config(self):
        config = super(CustomLSTM, self).get_config()
        config.pop('time_major', None)
        return config


# LSTM 모델 로드
# 현재 파일의 디렉토리를 기준으로 상대 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, 'theft_detection_lstm_model.h5')
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found: {model_path}")

model = tf.keras.models.load_model(model_path, custom_objects={
                                   'LSTM': CustomLSTM}, compile=False)


def upload_file_to_s3_2(file_path, bucket_name, s3_key):
    try:
        with open(file_path, 'rb') as file_obj:
            s3_client.upload_fileobj(file_obj, bucket_name, s3_key, ExtraArgs={
                'ContentType': 'video/mp4',
                'CacheControl': 'max-age=86400'
            })
        logger.info(f"Successfully uploaded {s3_key} to {bucket_name}")
        # 파일의 URL을 반환
        s3_url = f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
        return s3_url
    except Exception as e:
        logger.error(f"Error uploading file to S3: {e}")
        raise


def extract_features(pose_data):
    X = []
    frames = []
    for frame, poses in pose_data.items():
        frames.append(frame)
        for pose in poses:
            features = [lm['x'] for lm in pose] + [lm['y']
                                                   for lm in pose] + [lm['z'] for lm in pose]
            X.append(features)
    return np.array(X), frames


def create_sequences(data, frames, sequence_length):
    sequences = []
    sequence_frames = []
    for i in range(len(data) - sequence_length + 1):
        sequences.append(data[i:i + sequence_length])
        sequence_frames.append(frames[i:i + sequence_length])
    return np.array(sequences), sequence_frames


def process_video(url, s3_output_name, upload_time):
    print('process_video - try')

    # URL 파싱하여 S3 버킷 정보 추출
    parsed_url = urlparse(url)
    bucket_name = parsed_url.netloc.split('.')[0]
    s3_key = parsed_url.path.lstrip('/')

    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_input_file:
        local_file_name = temp_input_file.name

    try:
        s3_client.download_file(bucket_name, s3_key, local_file_name)
    except Exception as e:
        print(f"Error downloading file from S3: {e}")
        return s3_output_name, False
    # 로컬 파일을 사용하여 VideoCapture 객체 생성
    cap = cv2.VideoCapture(local_file_name)

    length = 10
    pose_data = {}

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_interval = int(fps / 3)  # 1초에 3프레임 간격 설정

    # 동영상 출력 설정
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    local_output_path = 'output.mp4'
    out = cv2.VideoWriter(local_output_path, fourcc, 10,
                          (width, height))  # FPS를 10으로 설정

    frame_count = 0
    all_frames = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            frame_name = f'frame_{frame_count // frame_interval:04d}.jpg'
            all_frames.append((frame_name, frame))

            # YOLO를 사용하여 사람만 탐지
            results_yolo = yolo_model.predict(frame, conf=0.5)
            people_boxes = [box for box in results_yolo[0].boxes if int(
                box.cls[0]) == 0]  # 사람만 선택

            if people_boxes:
                # 신뢰도가 가장 높은 바운딩 박스 선택
                best_box = max(people_boxes, key=lambda box: box.conf[0])
                x1, y1, x2, y2 = map(int, best_box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2),
                              (0, 255, 0), 2)  # 바운딩 박스 그리기

                # 바운딩 박스 내에서 포즈 추출
                roi = frame[y1:y2, x1:x2]
                image_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
                results = pose.process(image_rgb)

                if results.pose_landmarks:
                    pose_landmarks = results.pose_landmarks.landmark
                    xy_list = [
                        {'x': lm.x, 'y': lm.y, 'z': lm.z, 'visibility': lm.visibility} for idx, lm in enumerate(pose_landmarks)
                        if idx not in excluded_landmarks
                    ]

                    # 기존 데이터가 없는 경우 초기화
                    if frame_name not in pose_data:
                        pose_data[frame_name] = []
                    pose_data[frame_name].append(xy_list)

                    # 랜드마크 그리기
                    for idx, lm in enumerate(pose_landmarks):
                        if idx not in excluded_landmarks:
                            cx = int(lm.x * (x2 - x1) + x1)
                            cy = int(lm.y * (y2 - y1) + y1)
                            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

                    # 연결선 그리기
                    for connection in mp_pose.POSE_CONNECTIONS:
                        if connection[0] not in excluded_landmarks and connection[1] not in excluded_landmarks:
                            start_idx = connection[0]
                            end_idx = connection[1]
                            if pose_landmarks[start_idx].visibility > 0.5 and pose_landmarks[end_idx].visibility > 0.5:
                                start_point = (int(pose_landmarks[start_idx].x * (x2 - x1) + x1), int(
                                    pose_landmarks[start_idx].y * (y2 - y1) + y1))
                                end_point = (int(pose_landmarks[end_idx].x * (x2 - x1) + x1), int(
                                    pose_landmarks[end_idx].y * (y2 - y1) + y1))
                                cv2.line(frame, start_point,
                                         end_point, (0, 255, 0), 2)

        frame_count += 1

    cap.release()

    # 특징 추출
    try:
        X, frames = extract_features(pose_data)
    except Exception as e:
        print(f"Error in extracting features: {e}")
        return s3_output_name, False

    # 시퀀스 생성
    sequence_length = 10
    X_seq, sequence_frames = create_sequences(X, frames, sequence_length)

    # 예측
    if len(X_seq) == 0:
        return s3_output_name, False

    predictions = model.predict(X_seq)

    # 비디오 생성
    max_score_index = np.argmax(predictions[:, 1])
    max_score = predictions[max_score_index, 1]
    start_index = max(max_score_index - 30, 0)
    end_index = min(max_score_index + 30 +
                    sequence_length, len(all_frames) - 1)

    label = 'Theft' if max_score > 0.5 else 'Normal'
    color = (0, 0, 255) if max_score > 0.5 else (0, 255, 0)
    font_scale = 2  # 텍스트 크기 증가

    for i in range(start_index, end_index + 1):
        frame_name, frame = all_frames[i]
        out.write(frame)

    out.release()

    # 파일 존재 확인
    if not os.path.exists(local_output_path):
        print(f"Error: Output file {local_output_path} was not created")
        return s3_output_name, False

    # 이상 행동 감지 여부
    abnormal_behavior_detected = bool(max_score > 0.80)
    print(
        f's3_output_name: {s3_output_name}, \n local_output_path: {local_output_path}')

    try:
        upload_file_to_s3_2(local_output_path,
                            settings.AWS_STORAGE_BUCKET_NAME, s3_output_name)
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        return s3_output_name, False
    finally:
        # 임시 파일 삭제
        os.remove(local_file_name)
        os.remove(local_output_path)

    return abnormal_behavior_detected


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

        if not isinstance(abnormal_behavior_detected, bool):
            raise ValueError(f"Unexpected return value from process_video: {abnormal_behavior_detected}")

        video_instance.processed_video.name = s3_output_name
        video_instance.abnormal_behavior_detected = abnormal_behavior_detected
        video_instance.upload_time = upload_time
        video_instance.save()

        print(f"Video instance saved with processed video path: {video_instance.processed_video.name}")

        return True
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}", exc_info=True)
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
    sts_client = boto3.client(
        'sts',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    assumed_role_object = sts_client.assume_role(
        RoleArn="arn:aws:iam::000557732562:role/cross",
        RoleSessionName="AssumeRoleSession"
    )
    s3_client = boto3.client(
        's3',
        aws_access_key_id=assumed_role_object['Credentials']['AccessKeyId'],
        aws_secret_access_key=assumed_role_object['Credentials']['SecretAccessKey'],
        aws_session_token=assumed_role_object['Credentials']['SessionToken']
    )
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
