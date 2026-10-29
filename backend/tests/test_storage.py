"""Storage adapter tests without a MinIO server."""
from datetime import timedelta
from unittest.mock import MagicMock, patch
from app.core.storage import MinIOStorage
from app.core.config import settings


def test_lazy_client_and_upload() -> None:
    with patch('app.core.storage.Minio') as factory:
        storage = MinIOStorage()
        factory.assert_not_called()
        factory.return_value.bucket_exists.return_value = False
        assert storage.upload_file('key', b'pdf', 'application/pdf') == 'key'
        factory.return_value.make_bucket.assert_called_once_with(settings.MINIO_BUCKET)
        args, kwargs = factory.return_value.put_object.call_args
        assert args[:2] == (settings.MINIO_BUCKET, 'key')
        assert args[2].read() == b'pdf'
        assert args[3] == 3
        assert kwargs['content_type'] == 'application/pdf'
        storage.upload_file('other', b'x', 'image/png')
        factory.assert_called_once()


def test_presigned_and_delete() -> None:
    with patch('app.core.storage.Minio') as factory:
        storage = MinIOStorage()
        factory.return_value.presigned_get_object.return_value = 'https://storage.example/file'
        assert storage.get_presigned_url('key', 120) == 'https://storage.example/file'
        factory.return_value.presigned_get_object.assert_called_once_with(settings.MINIO_BUCKET, 'key', expires=timedelta(seconds=120))
        storage.delete_file('key')
        factory.return_value.remove_object.assert_called_once_with(settings.MINIO_BUCKET, 'key')
