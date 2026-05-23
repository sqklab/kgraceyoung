from __future__ import annotations
from pathlib import Path
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from app.core.config import get_settings

settings = get_settings()

def s3_client():
    return boto3.client(
        "s3",
        endpoint_url=("https://" if settings.minio_secure else "http://") + settings.minio_endpoint,
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )

def ensure_bucket(bucket: str | None = None) -> None:
    bucket_name = bucket or settings.minio_bucket_products
    client = s3_client()
    try:
        client.head_bucket(Bucket=bucket_name)
    except ClientError:
        client.create_bucket(Bucket=bucket_name)
    # MinIO public read policy for local development only.
    policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"AWS": ["*"]},
            "Action": ["s3:GetObject"],
            "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
        }]
    }
    import json
    try:
        client.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy))
    except Exception:
        pass

def upload_file(local_path: str | Path, key: str, content_type: str = "image/png", bucket: str | None = None) -> str:
    bucket_name = bucket or settings.minio_bucket_products
    ensure_bucket(bucket_name)
    client = s3_client()
    client.upload_file(
        str(local_path),
        bucket_name,
        key,
        ExtraArgs={"ContentType": content_type, "CacheControl": "public, max-age=31536000"},
    )
    return f"{settings.minio_public_endpoint.rstrip('/')}/{bucket_name}/{key}"
