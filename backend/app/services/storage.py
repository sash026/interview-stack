import logging
from typing import BinaryIO

import boto3
from botocore.client import BaseClient

from app.core.config import settings

logger = logging.getLogger(__name__)

_DEFAULT_PRESIGNED_URL_EXPIRY_SECONDS = 3600


def _get_s3_client() -> BaseClient:
    return boto3.client(
        "s3",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
    )


def upload_file(file_obj: BinaryIO, key: str, content_type: str | None = None) -> str:
    """Upload a file-like object to S3 and return the object key it was stored under."""
    extra_args = {"ContentType": content_type} if content_type else {}
    client = _get_s3_client()
    client.upload_fileobj(
        file_obj, settings.AWS_STORAGE_BUCKET_NAME, key, ExtraArgs=extra_args
    )
    logger.info("Uploaded object to s3://%s/%s", settings.AWS_STORAGE_BUCKET_NAME, key)
    return key


def delete_file(key: str) -> None:
    """Delete an object from S3 by key."""
    client = _get_s3_client()
    client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
    logger.info("Deleted object s3://%s/%s", settings.AWS_STORAGE_BUCKET_NAME, key)


def generate_presigned_upload_url(
    key: str,
    content_type: str | None = None,
    expires_in: int = _DEFAULT_PRESIGNED_URL_EXPIRY_SECONDS,
) -> str:
    """Generate a pre-signed URL the frontend can PUT a file to directly."""
    client = _get_s3_client()
    params = {"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": key}
    if content_type:
        params["ContentType"] = content_type
    return client.generate_presigned_url("put_object", Params=params, ExpiresIn=expires_in)


def generate_presigned_view_url(
    key: str, expires_in: int = _DEFAULT_PRESIGNED_URL_EXPIRY_SECONDS
) -> str:
    """Generate a pre-signed URL for temporarily viewing/downloading a file."""
    client = _get_s3_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": key},
        ExpiresIn=expires_in,
    )
