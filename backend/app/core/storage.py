"""Lazy MinIO storage; construction never requires a running server."""
from datetime import timedelta
from io import BytesIO
from functools import lru_cache

from minio import Minio

from app.core.config import settings


class MinIOStorage:
    def __init__(self) -> None:
        self._client: Minio | None = None

    def _get_client(self) -> Minio:
        if self._client is None:
            client = Minio(settings.MINIO_URL, access_key=settings.MINIO_ACCESS_KEY,
                           secret_key=settings.MINIO_SECRET_KEY, secure=settings.MINIO_SECURE)
            if not client.bucket_exists(settings.MINIO_BUCKET):
                client.make_bucket(settings.MINIO_BUCKET)
            self._client = client
        return self._client

    def upload_file(self, key: str, data: bytes, content_type: str) -> str:
        self._get_client().put_object(settings.MINIO_BUCKET, key, BytesIO(data),
                                      len(data), content_type=content_type)
        return key

    def get_presigned_url(self, key: str, expires_seconds: int = 3600) -> str:
        client = self._get_client()
        if settings.MINIO_PUBLIC_ENDPOINT:
            client = Minio(settings.MINIO_PUBLIC_ENDPOINT, access_key=settings.MINIO_ACCESS_KEY,
                           secret_key=settings.MINIO_SECRET_KEY, secure=settings.MINIO_PUBLIC_SECURE,
                           region=settings.MINIO_REGION)
        return client.presigned_get_object(
            settings.MINIO_BUCKET, key, expires=timedelta(seconds=expires_seconds))

    def delete_file(self, key: str) -> None:
        self._get_client().remove_object(settings.MINIO_BUCKET, key)


@lru_cache
def get_storage() -> MinIOStorage:
    return MinIOStorage()
