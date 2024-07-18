import boto3
from django.conf import settings


def list_processed_videos():
    s3 = boto3.client('s3',
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                      region_name=settings.AWS_S3_REGION_NAME)

    response = s3.list_objects_v2(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME, Prefix='videos/processed/')

    if 'Contents' in response:
        return [f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{obj['Key']}" for obj in response['Contents']]
    else:
        return []
