from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from botocore.exceptions import ClientError
from app.services.storage import s3_client

router = APIRouter(prefix="/assets", tags=["assets"])

@router.get("/{bucket}/{object_path:path}")
def get_asset(bucket: str, object_path: str):
    try:
        obj = s3_client().get_object(Bucket=bucket, Key=object_path)
    except ClientError as exc:
        raise HTTPException(status_code=404, detail="Asset not found") from exc
    content_type = obj.get("ContentType") or "application/octet-stream"
    headers = {"Cache-Control": "public, max-age=31536000"}
    return StreamingResponse(obj["Body"], media_type=content_type, headers=headers)
