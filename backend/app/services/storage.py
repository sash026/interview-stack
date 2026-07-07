import logging
import os
import tempfile
from typing import BinaryIO

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError

from app.core.config import settings
from app.services.exceptions import AudioNotFoundError

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


def download_to_tempfile(key: str) -> str:
    """Download an S3 object to a local temp file and return its path.

    Streams straight to disk via boto3's managed transfer rather than
    buffering the whole object in memory, so this is safe for large audio
    files. The caller owns the returned path and must remove it when done.
    """
    suffix = os.path.splitext(key)[1]
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)

    if not settings.AWS_ACCESS_KEY_ID:
        logger.warning(
            "AWS credentials not configured; mocking S3 download for key=%s", key
        )
        with open(path, "wb") as mock_file:
            mock_file.write(f"[mock audio bytes for {key}]".encode())
        return path

    client = _get_s3_client()
    try:
        client.download_file(settings.AWS_STORAGE_BUCKET_NAME, key, path)
    except ClientError as exc:
        os.remove(path)
        error_code = exc.response.get("Error", {}).get("Code")
        if error_code in ("404", "NoSuchKey"):
            raise AudioNotFoundError(f"Audio object not found in S3: {key}") from exc
        raise

    logger.info(
        "Downloaded object from s3://%s/%s", settings.AWS_STORAGE_BUCKET_NAME, key
    )
    return path
