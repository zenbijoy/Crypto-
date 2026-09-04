"""
CryptoScope AI - Object Storage Service
Implements Phase 20, 21, 42:
- Provider abstraction supporting S3, Cloudflare R2, and MinIO
- Parquet quant datasets storage and partitioned key resolution (provider=/symbol=/date=)
- Model artifacts, backtest research reports, and chart storage
- Presigned URL generation for private access
- Graceful local filesystem fallback when external object storage is not configured
"""
import os
import io
import logging
from typing import Optional, Dict, Any, Union
from datetime import datetime, timezone
from core.config import settings

logger = logging.getLogger("cryptoscope.storage")

class ObjectStorageService:
    def __init__(self):
        self.provider = settings.OBJECT_STORAGE_PROVIDER.lower()
        self.bucket = settings.S3_BUCKET
        self.endpoint_url = settings.S3_ENDPOINT
        self.access_key = settings.S3_ACCESS_KEY
        self.secret_key = settings.S3_SECRET_KEY
        self.region = settings.S3_REGION
        self.is_configured = bool(self.access_key and self.secret_key)
        self._s3_client = None

        if self.is_configured:
            try:
                import boto3
                self._s3_client = boto3.client(
                    "s3",
                    endpoint_url=self.endpoint_url,
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                    region_name=self.region
                )
                logger.info(f"ObjectStorageService initialized with {self.provider} on bucket {self.bucket}")
            except Exception as e:
                logger.warning(f"Failed to initialize S3/R2 client: {str(e)}")
                self.is_configured = False

    def build_parquet_key(self, provider: str, symbol: str, date_str: str, event_type: str = "candles") -> str:
        """Generates a partitioned key: provider=X/symbol=Y/date=Z/event_type.parquet"""
        return f"datasets/provider={provider}/symbol={symbol}/date={date_str}/{event_type}.parquet"

    async def put_object(self, key: str, data: Union[bytes, io.BytesIO], content_type: str = "application/octet-stream") -> Dict[str, Any]:
        """Uploads object data to bucket or local fallback directory."""
        if isinstance(data, io.BytesIO):
            data = data.getvalue()

        if self.is_configured and self._s3_client:
            try:
                self._s3_client.put_object(
                    Bucket=self.bucket,
                    Key=key,
                    Body=data,
                    ContentType=content_type
                )
                return {"status": "UPLOADED", "key": key, "bucket": self.bucket, "provider": self.provider}
            except Exception as e:
                logger.error(f"Failed to upload {key} to {self.bucket}: {str(e)}")
                return {"status": "FAILED", "error": str(e)}
        else:
            # Local filesystem fallback for dev
            local_path = os.path.join("./storage_data", key)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(data)
            return {"status": "STORED_LOCALLY", "path": local_path, "provider": "LOCAL_DEV"}

    async def get_object(self, key: str) -> Optional[bytes]:
        """Retrieves object data from bucket or local fallback."""
        if self.is_configured and self._s3_client:
            try:
                response = self._s3_client.get_object(Bucket=self.bucket, Key=key)
                return response["Body"].read()
            except Exception as e:
                logger.error(f"Error fetching {key}: {str(e)}")
                return None
        else:
            local_path = os.path.join("./storage_data", key)
            if os.path.exists(local_path):
                with open(local_path, "rb") as f:
                    return f.read()
            return None

    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> Optional[str]:
        """Generates a secure presigned URL for private artifact download."""
        if self.is_configured and self._s3_client:
            try:
                url = self._s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket, "Key": key},
                    ExpiresIn=expires_in
                )
                return url
            except Exception as e:
                logger.error(f"Presigned URL generation error: {str(e)}")
                return None
        return None

object_storage_service = ObjectStorageService()
