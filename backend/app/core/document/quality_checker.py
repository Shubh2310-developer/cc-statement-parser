"""PDF quality assessment."""
from app.core.extraction.text_extractor import TextExtractor
from app.utils.logger import get_logger

logger = get_logger(__name__)


class QualityChecker:
    """Assess PDF quality."""

    def __init__(self):
        self.text_extractor = TextExtractor()

    def check_quality(self, pdf_bytes: bytes) -> float:
        """
        Check PDF quality.

        Args:
            pdf_bytes: PDF content

        Returns:
            Quality score 0.0-1.0
        """
        logger.debug("Checking PDF quality")

        try:
            extracted = self.text_extractor.extract(pdf_bytes)
            
            if not extracted.pages:
                return 0.0

            # Calculate text density
            total_chars = sum(len(p.full_text) for p in extracted.pages)
            avg_chars_per_page = total_chars / len(extracted.pages)

            # Score based on text density
            if avg_chars_per_page > 1000:
                return 0.95  # Excellent
            elif avg_chars_per_page > 500:
                return 0.85  # Good
            elif avg_chars_per_page > 100:
                return 0.65  # Fair (might be scanned)
            else:
                return 0.40  # Poor (likely scanned)

        except Exception as e:
            logger.warning(f"Quality check failed: {e}")
            return 0.5
