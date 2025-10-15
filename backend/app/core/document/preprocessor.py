"""PDF preprocessing."""
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentPreprocessor:
    """Preprocess PDFs before extraction."""

    def preprocess(self, pdf_bytes: bytes) -> bytes:
        """
        Preprocess PDF.

        Args:
            pdf_bytes: Original PDF bytes

        Returns:
            Processed PDF bytes
        """
        logger.debug("Preprocessing PDF")
        # For now, just return as-is
        # Could add: decryption, optimization, etc.
        return pdf_bytes
