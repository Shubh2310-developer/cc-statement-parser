"""Confidence scoring for extracted fields."""
from app.models.domain.field import Field
from app.models.domain.extraction_result import ExtractionResult
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ConfidenceScorer:
    """Calculate confidence scores for extraction."""

    def calculate_confidence(self, field: Field) -> float:
        """
        Calculate confidence for a single field.

        Args:
            field: Field to score

        Returns:
            Confidence score 0.0-1.0
        """
        base_confidence = field.confidence

        # Adjust based on extraction method
        if field.extraction_method == "regex":
            base_confidence *= 1.0
        elif field.extraction_method == "ocr":
            base_confidence *= 0.8
        elif field.extraction_method == "ml_model":
            base_confidence *= 0.95

        # Adjust based on field type
        if field.field_type.is_sensitive:
            base_confidence *= 0.95  # Be more conservative

        return min(1.0, base_confidence)

    def calculate_overall_confidence(self, result: ExtractionResult) -> float:
        """
        Calculate overall confidence for extraction result.

        Args:
            result: Extraction result

        Returns:
            Overall confidence score
        """
        if not result.fields:
            return 0.0

        # Calculate average confidence
        confidences = [self.calculate_confidence(f) for f in result.fields.values()]
        avg_confidence = sum(confidences) / len(confidences)

        # Adjust based on completeness
        completeness = result.field_count / 10  # Assume 10 important fields
        completeness_factor = min(1.0, completeness)

        overall = avg_confidence * 0.7 + completeness_factor * 0.3

        logger.debug(f"Overall confidence: {overall:.2f}")
        return overall
