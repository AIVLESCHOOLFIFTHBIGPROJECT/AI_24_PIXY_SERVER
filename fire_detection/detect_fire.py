import cv2
from ultralytics import YOLO
import os
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from urllib.parse import urlparse
from venv import logger
import tempfile

sts_client = boto3.client(
    'sts',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

assumed_role_object = sts_client.assume_role(
    RoleArn= settings.S3_ROLE_ARN,
    RoleSessionName="AssumeRoleSession"
)

s3 = boto3.client(
    's3',
    aws_access_key_id=assumed_role_object['Credentials']['AccessKeyId'],
    aws_secret_access_key=assumed_role_object['Credentials']['SecretAccessKey'],
    aws_session_token=assumed_role_object['Credentials']['SessionToken'],
    region_name= settings.AWS_REGION
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

# def download_file_from_s3(bucket_name, s3_key, local_path):
#     try:
#         if not s3_key.startswith('media/'):
#             s3_key = f'media/{s3_key}'
#         print(f"Attempting to download from bucket: {bucket_name}, key: {s3_key}")
        
#         with open(local_path, 'wb') as f:
#             s3.download_fileobj(bucket_name, s3_key, f)
#         print(f"Successfully downloaded file to {local_path}")
#     except Exception as e:
#         print(f"Error downloading file from S3: {str(e)}")
#         raise

# def download_file_from_s3(bucket_name, s3_url, local_path):
#     try:
#         parsed_url = urlparse(s3_url)
#         s3_key = parsed_url.path.lstrip('/')
#         if not s3_key.startswith('media/'):
#             s3_key = f'media/{s3_key}'
#         print(f"Attempting to download from bucket: {bucket_name}, key: {s3_key}")
        
#         # 파일 존재 여부 확인
#         try:
#             s3.head_object(Bucket=bucket_name, Key=s3_key)
#         except ClientError as e:
#             if e.response['Error']['Code'] == "404":
#                 print(f"The object does not exist. Bucket: {bucket_name}, Key: {s3_key}")
#             else:
#                 print(f"An error occurred while checking object existence: {str(e)}")
#             raise

#         with open(local_path, 'wb') as f:
#             s3.download_fileobj(bucket_name, s3_key, f)
#         print(f"Successfully downloaded file to {local_path}")
#     except Exception as e:
#         print(f"Error downloading file from S3: {str(e)}")
#         raise


# def upload_file_to_s3(file_obj, bucket_name, s3_key):
#     try:
#         s3.upload_fileobj(file_obj, bucket_name, s3_key, ExtraArgs={
#             'ContentType': 'video/mp4',
#             'CacheControl': 'max-age=86400'
#         })
#         print(f's3_key: {s3_key}, bucket_name: {bucket_name}')
#         logger.info(f"Successfully uploaded {s3_key} to {bucket_name}")
#         # 파일의 URL을 반환
#         s3_url = f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
#         logger.info(f"Uploaded file URL: {s3_url}")  # URL을 로그에 출력
#         return s3_url
#     except Exception as e:
#         logger.error(f"Error uploading file to S3: {e}")
#         raise


def upload_file_to_s3_2(file_path, bucket_name, s3_key):
    try:
        with open(file_path, 'rb') as file_obj:
            s3.upload_fileobj(file_obj, bucket_name, s3_key, ExtraArgs={
                'ContentType': 'video/mp4',
                'CacheControl': 'max-age=86400'
            })
        logger.info(f"Successfully uploaded {s3_key} to {bucket_name}")
        # 파일의 URL을 반환
        s3_url = f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
        print(f"Uploaded file URL: {s3_url}")  # URL을 로그에 출력
        return s3_url
    except Exception as e:
        logger.error(f"Error uploading file to S3: {e}")
        raise

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, 'fire_yolov8n_v2.pt')
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found: {model_path}")

def detect_fire(s3_input_url, s3_output_name, upload_time):
    
    model = YOLO(model_path)
    
    parsed_url = urlparse(s3_input_url)
    bucket_name = parsed_url.netloc.split('.')[0]
    s3_key = parsed_url.path.lstrip('/')
    
    # parsed_url = urlparse(s3_input_url)
    # s3_key = parsed_url.path.lstrip('/')
    # if not s3_key.startswith('media/'):
    # s3_key = f'media/{s3_key}'
    
    with tempfile.NamedTemporaryFile(suffix = '.mp4', delete = False) as temp_input_file:
        local_file_name = temp_input_file.name
    
    try:
        s3.download_file(bucket_name, s3_key, local_file_name)
    except Exception as e:
        print(f"Error downloading file from S3: {e}")
        return s3_output_name, False
    
    # 로컬 파일을 이용해 VideoCapture 객체 생성
    cap = cv2.VideoCapture(local_file_name)    

    # 비디오 속성 추출
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    
    with tempfile.NamedTemporaryFile(suffix = '.mp4', delete = False) as temp_output_file:
        local_output_path = temp_output_file.name
        
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
    
    if not os.path.exists(local_output_path):
        print(f"Error: Output file {local_output_path} was not created")
        return s3_output_name, False
    
    # print(f's3_output_name: {s3_output_name}, \n local_input_path: {local_output_path}')
    
    # upload_file_to_s3_2(local_output_path,
    #                     settings.AWS_STORAGE_BUCKET_NAME, s3_output_name)

    # os.remove(local_file_name)
    # os.remove(local_output_path)

    # return fire_detected
    
    print(f's3_output_name: {s3_output_name}, \n local_output_path: {local_output_path}')

    try:
        upload_file_to_s3_2(local_output_path, settings.AWS_STORAGE_BUCKET_NAME, s3_output_name)
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        return s3_output_name, False
    finally:
        # 임시 파일 삭제
        os.remove(local_file_name)
        os.remove(local_output_path)

    return fire_detected

