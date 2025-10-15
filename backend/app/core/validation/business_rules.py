"""Business rule validation."""
from datetime import datetime, timedelta
from typing import List

from app.models.domain.extraction_result import ExtractionResult
from app.models.enums import FieldType
from app.utils.logger import get_logger
from app.utils.date_parser import parse_date

logger = get_logger(__name__)


class BusinessRulesValidator:
    """Validate business rules."""

    def validate_business_rules(self, result: ExtractionResult) -> List[str]:
        """
        Validate business rules.

        Args:
            result: Extraction result

        Returns:
            List of validation error messages
        """
        errors = []

        # Validate due date is in future or recent past
        if result.has_field(FieldType.PAYMENT_DUE_DATE):
            due_date_str = result.get_field_value(FieldType.PAYMENT_DUE_DATE)
            if due_date_str:
                due_date = parse_date(due_date_str)
                if due_date:
                    days_diff = (due_date - datetime.now()).days
                    if days_diff < -90 or days_diff > 90:
                        errors.append("Due date seems unrealistic (too far in past or future)")

        # Validate amounts are positive
        for field_type in [FieldType.TOTAL_AMOUNT_DUE, FieldType.MINIMUM_AMOUNT_DUE]:
            if result.has_field(field_type):
                amount = result.get_field_value(field_type)
                if amount is not None and amount < 0:
                    errors.append(f"{field_type.value} should not be negative")

        # Validate minimum <= total
        if result.has_field(FieldType.TOTAL_AMOUNT_DUE) and result.has_field(FieldType.MINIMUM_AMOUNT_DUE):
            total = result.get_field_value(FieldType.TOTAL_AMOUNT_DUE)
            minimum = result.get_field_value(FieldType.MINIMUM_AMOUNT_DUE)
            if total is not None and minimum is not None and minimum > total:
                errors.append("Minimum amount due cannot exceed total amount due")

        logger.debug(f"Business rules validation: {len(errors)} errors")
        return errors
