"""Storage module."""
from app.storage.base import StorageBackend
from app.storage.local_storage import LocalStorage
from app.storage.s3_storage import S3Storage

__all__ = ['StorageBackend', 'LocalStorage', 'S3Storage']
