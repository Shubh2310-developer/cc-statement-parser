"""ExtractionResult domain model.

This module defines the ExtractionResult model representing
the complete results of parsing a credit card statement.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from .field import Field
from ..enums import FieldType, IssuerType


@dataclass
class ExtractionResult:
    """Represents the complete extraction result from a credit card statement.

    Attributes:
        id: Unique result identifier
        job_id: ID of the associated job
        document_id: ID of the associated document
        issuer: Detected credit card issuer
        fields: Dictionary of extracted fields by field type
        raw_text: Raw text extracted from the PDF
        extraction_metadata: Metadata about the extraction process
        created_at: Timestamp when the result was created
        confidence_score: Overall confidence score (0.0 to 1.0)
    """

    id: str
    job_id: str
    document_id: str
    issuer: IssuerType
    fields: dict[FieldType, Field] = field(default_factory=dict)
    raw_text: Optional[str] = None
    extraction_metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    confidence_score: float = 0.0

    def __post_init__(self):
        """Validate result after initialization."""
        # Ensure confidence is between 0 and 1
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError(
                f"Confidence score must be between 0.0 and 1.0, got {self.confidence_score}"
            )

    def add_field(self, field: Field) -> "ExtractionResult":
        """Add a field to the extraction result.

        Args:
            field: Field to add

        Returns:
            Updated ExtractionResult instance
        """
        self.fields[field.field_type] = field
        self._recalculate_confidence()
        return self

    def get_field(self, field_type: FieldType) -> Optional[Field]:
        """Get a field by type.

        Args:
            field_type: Type of field to retrieve

        Returns:
            Field if found, None otherwise
        """
        return self.fields.get(field_type)

    def get_field_value(
        self,
        field_type: FieldType,
        default: Any = None,
    ) -> Any:
        """Get the value of a field.

        Args:
            field_type: Type of field to retrieve
            default: Default value if field not found

        Returns:
            Field value or default
        """
        field = self.get_field(field_type)
        return field.value if field else default

    def has_field(self, field_type: FieldType) -> bool:
        """Check if a field exists.

        Args:
            field_type: Type of field to check

        Returns:
            True if field exists, False otherwise
        """
        return field_type in self.fields

    def get_high_confidence_fields(self, threshold: float = 0.7) -> dict[FieldType, Field]:
        """Get fields with confidence above threshold.

        Args:
            threshold: Confidence threshold

        Returns:
            Dictionary of high-confidence fields
        """
        return {
            field_type: field
            for field_type, field in self.fields.items()
            if field.confidence >= threshold
        }

    def get_low_confidence_fields(self, threshold: float = 0.7) -> dict[FieldType, Field]:
        """Get fields with confidence below threshold.

        Args:
            threshold: Confidence threshold

        Returns:
            Dictionary of low-confidence fields
        """
        return {
            field_type: field
            for field_type, field in self.fields.items()
            if field.confidence < threshold
        }

    def get_fields_by_category(self, category: str) -> dict[FieldType, Field]:
        """Get fields by category (amounts, dates, etc.).

        Args:
            category: Category name ('amount', 'date', 'sensitive')

        Returns:
            Dictionary of fields matching the category
        """
        if category == "amount":
            return {
                field_type: field
                for field_type, field in self.fields.items()
                if field_type.is_amount
            }
        elif category == "date":
            return {
                field_type: field
                for field_type, field in self.fields.items()
                if field_type.is_date
            }
        elif category == "sensitive":
            return {
                field_type: field
                for field_type, field in self.fields.items()
                if field_type.is_sensitive
            }
        else:
            return {}

    def _recalculate_confidence(self) -> None:
        """Recalculate overall confidence score based on fields."""
        if not self.fields:
            self.confidence_score = 0.0
            return

        # Calculate average confidence of all fields
        total_confidence = sum(field.confidence for field in self.fields.values())
        self.confidence_score = total_confidence / len(self.fields)

    def add_metadata(self, key: str, value: Any) -> "ExtractionResult":
        """Add metadata to the extraction result.

        Args:
            key: Metadata key
            value: Metadata value

        Returns:
            Updated ExtractionResult instance
        """
        self.extraction_metadata[key] = value
        return self

    def to_dict(self) -> dict:
        """Convert extraction result to dictionary.

        Returns:
            Dictionary representation of the result
        """
        return {
            "id": self.id,
            "job_id": self.job_id,
            "document_id": self.document_id,
            "issuer": str(self.issuer),
            "fields": {
                str(field_type): field.to_dict()
                for field_type, field in self.fields.items()
            },
            "raw_text": self.raw_text,
            "extraction_metadata": self.extraction_metadata,
            "created_at": self.created_at.isoformat(),
            "confidence_score": self.confidence_score,
            "field_count": len(self.fields),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ExtractionResult":
        """Create extraction result from dictionary.

        Args:
            data: Dictionary containing result data

        Returns:
            ExtractionResult instance
        """
        # Convert issuer from string
        issuer = data.get("issuer", IssuerType.UNKNOWN)
        if isinstance(issuer, str):
            issuer = IssuerType(issuer)

        # Parse created_at
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.utcnow()

        # Convert fields dictionary
        fields = {}
        if "fields" in data:
            for field_type_str, field_data in data["fields"].items():
                field_type = FieldType(field_type_str)
                fields[field_type] = Field.from_dict(field_data)

        return cls(
            id=data["id"],
            job_id=data["job_id"],
            document_id=data["document_id"],
            issuer=issuer,
            fields=fields,
            raw_text=data.get("raw_text"),
            extraction_metadata=data.get("extraction_metadata", {}),
            created_at=created_at,
            confidence_score=data.get("confidence_score", 0.0),
        )

    def to_simple_dict(self) -> dict:
        """Convert to a simplified dictionary with just field values.

        Returns:
            Simplified dictionary with field names as keys and values
        """
        return {
            str(field_type): field.value
            for field_type, field in self.fields.items()
        }

    @property
    def has_high_confidence(self, threshold: float = 0.7) -> bool:
        """Check if overall confidence is high.

        Args:
            threshold: Confidence threshold

        Returns:
            True if confidence >= threshold
        """
        return self.confidence_score >= threshold

    @property
    def field_count(self) -> int:
        """Get count of extracted fields.

        Returns:
            Number of fields
        """
        return len(self.fields)

    def __repr__(self) -> str:
        """String representation of the extraction result.

        Returns:
            String representation
        """
        return (
            f"ExtractionResult(id={self.id}, "
            f"issuer={self.issuer}, "
            f"fields={len(self.fields)}, "
            f"confidence={self.confidence_score:.2f})"
        )
