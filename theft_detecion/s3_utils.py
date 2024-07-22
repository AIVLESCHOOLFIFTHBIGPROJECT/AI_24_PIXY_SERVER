import boto3
from django.conf import settings


def list_processed_videos():
    sts_client = boto3.client('sts')
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

    response = s3_client.list_objects_v2(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME, Prefix='media/videos/processed/')

    if 'Contents' in response:
        video_urls = [
            f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{obj['Key']}" for obj in response['Contents']]
        print(f"Processed videos: {video_urls}")
        return video_urls
    else:
        return []
