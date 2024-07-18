import boto3
from django.conf import settings


def list_processed_videos():
    s3 = boto3.client('s3',
                      aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
                      region_name=settings.AWS_REGION)

    response = s3.list_objects_v2(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME, Prefix='media/videos/processed/')

    if 'Contents' in response:
        video_urls = [
            f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{obj['Key']}" for obj in response['Contents']]
        print(f"Processed videos: {video_urls}")
        return video_urls
    else:
        return []
