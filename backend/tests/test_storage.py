from unittest.mock import patch
from datetime import timedelta
from app.core.storage import MinIOStorage
from app.core.config import settings


def test_lazy_client_and_bucket() -> None:
    with patch("app.core.storage.Minio") as factory:
        storage = MinIOStorage()
        factory.assert_not_called()
        factory.return_value.bucket_exists.return_value = False
        assert storage.upload_file("key", b"data", "application/pdf") == "key"
        storage.upload_file("next", b"next", "application/pdf")
        factory.return_value.make_bucket.assert_called_once_with(settings.MINIO_BUCKET)
        args = factory.return_value.put_object.call_args
        assert args.args[2].read() == b"next"
        assert args.args[3] == 4


def test_presign_and_delete() -> None:
    with patch("app.core.storage.Minio") as factory:
        storage = MinIOStorage()
        factory.return_value.presigned_get_object.return_value = "signed"
        assert storage.get_presigned_url("key", 120) == "signed"
        factory.return_value.presigned_get_object.assert_called_once_with(
            settings.MINIO_BUCKET, "key", expires=timedelta(seconds=120))
        storage.delete_file("key")
        factory.return_value.remove_object.assert_called_once_with(settings.MINIO_BUCKET, "key")


def test_existing_bucket_is_not_recreated() -> None:
    with patch("app.core.storage.Minio") as factory:
        factory.return_value.bucket_exists.return_value = True
        MinIOStorage().upload_file("key", b"data", "image/png")
        factory.return_value.make_bucket.assert_not_called()
