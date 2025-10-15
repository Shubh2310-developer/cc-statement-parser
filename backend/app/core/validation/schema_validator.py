"""Schema validation for extraction results."""
from typing import List
from dataclasses import dataclass

from app.models.domain.extraction_result import ExtractionResult
from app.models.enums import FieldType
from app.models.schemas.internal import ValidationResult
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationError:
    field: str
    message: str
    severity: str = "error"  # error, warning


class SchemaValidator:
    """Validate extraction results against schema."""

    REQUIRED_FIELDS = [
        FieldType.CARD_LAST_4_DIGITS,
        FieldType.PAYMENT_DUE_DATE,
        FieldType.TOTAL_AMOUNT_DUE,
    ]

    def validate(self, extraction_result: ExtractionResult) -> ValidationResult:
        """
        Validate extraction result.

        Args:
            extraction_result: Extraction result to validate

        Returns:
            ValidationResult with validation status
        """
        logger.debug("Validating extraction result")

        errors = []
        warnings = []

        # Check required fields
        for field_type in self.REQUIRED_FIELDS:
            if not extraction_result.has_field(field_type):
                errors.append(ValidationError(
                    field=field_type.value,
                    message=f"Required field {field_type.value} is missing",
                    severity="error"
                ))

        # Check field values
        for field in extraction_result.fields.values():
            if field.value is None or field.value == "":
                warnings.append(ValidationError(
                    field=field.field_type.value,
                    message="Field has empty value",
                    severity="warning"
                ))

        is_valid = len(errors) == 0
        
        logger.info(f"Validation result: valid={is_valid}, errors={len(errors)}, warnings={len(warnings)}")

        # Store additional info in metadata
        metadata = {
            'field_count': extraction_result.field_count,
            'completeness_score': self._calculate_completeness(extraction_result)
        }

        return ValidationResult(
            is_valid=is_valid,
            errors=[e.message for e in errors],
            warnings=[w.message for w in warnings],
            metadata=metadata
        )

    def _calculate_completeness(self, result: ExtractionResult) -> float:
        """Calculate completeness score (0-1)."""
        total_possible_fields = len(FieldType)
        fields_extracted = result.field_count
        return min(1.0, fields_extracted / (total_possible_fields * 0.5))
