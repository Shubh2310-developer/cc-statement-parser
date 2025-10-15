"""Base storage interface."""
from abc import ABC, abstractmethod
from pathlib import Path


class StorageBackend(ABC):
    """Abstract storage backend interface."""

    @abstractmethod
    async def save(self, file_id: str, content: bytes) -> str:
        """Save file and return path."""
        pass

    @abstractmethod
    async def load(self, path: str) -> bytes:
        """Load file content."""
        pass

    @abstractmethod
    async def delete(self, path: str) -> bool:
        """Delete file."""
        pass

    @abstractmethod
    async def exists(self, path: str) -> bool:
        """Check if file exists."""
        pass
