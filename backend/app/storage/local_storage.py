"""Local filesystem storage."""
import aiofiles
from pathlib import Path

from app.storage.base import StorageBackend
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class LocalStorage(StorageBackend):
    """Local filesystem storage implementation."""

    def __init__(self, base_dir: Path = None):
        self.base_dir = Path(base_dir) if base_dir else settings.UPLOAD_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, file_id: str, content: bytes) -> str:
        """Save file to local filesystem."""
        file_path = self.base_dir / f"{file_id}.pdf"
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        logger.info(f"Saved file to {file_path}")
        return str(file_path)

    async def load(self, path: str) -> bytes:
        """Load file from filesystem."""
        async with aiofiles.open(path, 'rb') as f:
            content = await f.read()
        return content

    async def delete(self, path: str) -> bool:
        """Delete file."""
        try:
            Path(path).unlink()
            logger.info(f"Deleted file {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete {path}: {e}")
            return False

    async def exists(self, path: str) -> bool:
        """Check if file exists."""
        return Path(path).exists()
