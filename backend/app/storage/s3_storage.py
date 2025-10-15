"""S3-compatible storage (stub)."""
from app.storage.base import StorageBackend
from app.utils.exceptions import StorageError


class S3Storage(StorageBackend):
    """S3 storage implementation (stub for future)."""

    async def save(self, file_id: str, content: bytes) -> str:
        raise NotImplementedError("S3 storage not yet implemented")

    async def load(self, path: str) -> bytes:
        raise NotImplementedError("S3 storage not yet implemented")

    async def delete(self, path: str) -> bool:
        raise NotImplementedError("S3 storage not yet implemented")

    async def exists(self, path: str) -> bool:
        raise NotImplementedError("S3 storage not yet implemented")
