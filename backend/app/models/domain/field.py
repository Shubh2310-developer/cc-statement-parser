"""Field domain model.

This module defines the Field model representing an extracted field
from a credit card statement with its value, confidence, and metadata.
"""

from dataclasses import dataclass, field
from typing import Any, Optional

from ..enums import FieldType


@dataclass
class BoundingBox:
    """Bounding box coordinates for text location in a PDF."""

    x0: float
    y0: float
    x1: float
    y1: float
    page: int = 0

    @property
    def width(self) -> float:
        """Calculate width of the bounding box.

        Returns:
            Width in points
        """
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        """Calculate height of the bounding box.

        Returns:
            Height in points
        """
        return self.y1 - self.y0

    @property
    def area(self) -> float:
        """Calculate area of the bounding box.

        Returns:
            Area in square points
        """
        return self.width * self.height

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "x0": self.x0,
            "y0": self.y0,
            "x1": self.x1,
            "y1": self.y1,
            "page": self.page,
            "width": self.width,
            "height": self.height,
        }


@dataclass
class Field:
    """Represents an extracted field from a credit card statement.

    Attributes:
        field_type: Type of the field (e.g., CARD_NUMBER, TOTAL_AMOUNT_DUE)
        value: Extracted value (can be any type)
        confidence: Confidence score (0.0 to 1.0)
        raw_value: Original raw value before parsing/normalization
        snippet: Text snippet containing the field from the document
        bounding_box: Location of the field in the PDF
        extraction_method: Method used to extract this field
        metadata: Additional metadata about the extraction
    """

    field_type: FieldType
    value: Any
    confidence: float = 0.0
    raw_value: Optional[str] = None
    snippet: Optional[str] = None
    bounding_box: Optional[BoundingBox] = None
    extraction_method: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        """Validate field after initialization."""
        # Ensure confidence is between 0 and 1
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")

        # Store raw_value if not provided
        if self.raw_value is None and self.value is not None:
            self.raw_value = str(self.value)

    @property
    def is_high_confidence(self, threshold: float = 0.7) -> bool:
        """Check if field has high confidence.

        Args:
            threshold: Confidence threshold (default 0.7)

        Returns:
            True if confidence >= threshold, False otherwise
        """
        return self.confidence >= threshold

    @property
    def display_value(self) -> str:
        """Get a display-friendly string representation of the value.

        Returns:
            String representation of the value
        """
        if self.value is None:
            return "N/A"
        return str(self.value)

    def to_dict(self) -> dict:
        """Convert field to dictionary.

        Returns:
            Dictionary representation of the field
        """
        # Convert Decimal to float for JSON serialization
        from decimal import Decimal
        value = self.value
        if isinstance(value, Decimal):
            value = float(value)

        return {
            "field_type": str(self.field_type),
            "value": value,
            "confidence": self.confidence,
            "raw_value": self.raw_value,
            "snippet": self.snippet,
            "bounding_box": self.bounding_box.to_dict() if self.bounding_box else None,
            "extraction_method": self.extraction_method,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Field":
        """Create field from dictionary.

        Args:
            data: Dictionary containing field data

        Returns:
            Field instance
        """
        # Convert bounding_box if present
        bounding_box = None
        if data.get("bounding_box"):
            bbox_data = data["bounding_box"]
            bounding_box = BoundingBox(
                x0=bbox_data["x0"],
                y0=bbox_data["y0"],
                x1=bbox_data["x1"],
                y1=bbox_data["y1"],
                page=bbox_data.get("page", 0),
            )

        # Convert field_type from string if necessary
        field_type = data["field_type"]
        if isinstance(field_type, str):
            field_type = FieldType(field_type)

        return cls(
            field_type=field_type,
            value=data["value"],
            confidence=data.get("confidence", 0.0),
            raw_value=data.get("raw_value"),
            snippet=data.get("snippet"),
            bounding_box=bounding_box,
            extraction_method=data.get("extraction_method"),
            metadata=data.get("metadata", {}),
        )

    def with_confidence(self, confidence: float) -> "Field":
        """Create a copy of the field with updated confidence.

        Args:
            confidence: New confidence value

        Returns:
            New Field instance with updated confidence
        """
        return Field(
            field_type=self.field_type,
            value=self.value,
            confidence=confidence,
            raw_value=self.raw_value,
            snippet=self.snippet,
            bounding_box=self.bounding_box,
            extraction_method=self.extraction_method,
            metadata=self.metadata.copy(),
        )

    def with_metadata(self, **kwargs) -> "Field":
        """Create a copy of the field with additional metadata.

        Args:
            **kwargs: Metadata key-value pairs to add

        Returns:
            New Field instance with updated metadata
        """
        new_metadata = self.metadata.copy()
        new_metadata.update(kwargs)

        return Field(
            field_type=self.field_type,
            value=self.value,
            confidence=self.confidence,
            raw_value=self.raw_value,
            snippet=self.snippet,
            bounding_box=self.bounding_box,
            extraction_method=self.extraction_method,
            metadata=new_metadata,
        )

    def __repr__(self) -> str:
        """String representation of the field.

        Returns:
            String representation
        """
        return (
            f"Field(type={self.field_type}, "
            f"value={self.value}, "
            f"confidence={self.confidence:.2f})"
        )
