"""Object storage, initialized only when a document operation needs it."""
from datetime import timedelta
from io import BytesIO
from functools import lru_cache
from minio import Minio
from minio.error import S3Error
from app.core.config import settings


class MinIOStorage:
    def __init__(self) -> None:
        self._client: Minio | None = None
        self._bucket_ready = False

    @property
    def client(self) -> Minio:
        if self._client is None:
            self._client = Minio(settings.MINIO_URL, access_key=settings.MINIO_ACCESS_KEY,
                                 secret_key=settings.MINIO_SECRET_KEY, secure=settings.MINIO_SECURE)
        return self._client

    def _ensure_bucket(self) -> None:
        if not self._bucket_ready:
            if not self.client.bucket_exists(settings.MINIO_BUCKET):
                try:
                    self.client.make_bucket(settings.MINIO_BUCKET)
                except S3Error as exc:
                    if exc.code != "BucketAlreadyOwnedByYou":
                        raise
            self._bucket_ready = True

    def upload_file(self, key: str, data: bytes, content_type: str) -> str:
        self._ensure_bucket()
        self.client.put_object(settings.MINIO_BUCKET, key, BytesIO(data), len(data),
                               content_type=content_type)
        return key

    def get_presigned_url(self, key: str, expires_seconds: int = 3600) -> str:
        return self.client.presigned_get_object(settings.MINIO_BUCKET, key,
                                                expires=timedelta(seconds=expires_seconds))

    def delete_file(self, key: str) -> None:
        self.client.remove_object(settings.MINIO_BUCKET, key)


@lru_cache
def get_storage() -> MinIOStorage:
    return MinIOStorage()
