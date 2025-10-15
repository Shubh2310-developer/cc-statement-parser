"""Request Pydantic schemas.

This module defines Pydantic models for API request validation.
"""

from typing import Optional

from pydantic import BaseModel, Field, field_validator

from ..enums import IssuerType


class ParseRequest(BaseModel):
    """Request schema for parsing a credit card statement.

    This is used when additional options need to be specified
    along with the file upload.
    """

    force_ocr: bool = Field(
        default=False,
        description="Force OCR processing even if text is extractable",
    )
    issuer_hint: Optional[IssuerType] = Field(
        default=None,
        description="Hint about the expected issuer to improve extraction",
    )
    confidence_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for field extraction",
    )
    include_raw_text: bool = Field(
        default=False,
        description="Include raw extracted text in the response",
    )
    mask_sensitive: bool = Field(
        default=True,
        description="Mask sensitive information in the response",
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "force_ocr": False,
                "issuer_hint": "hdfc",
                "confidence_threshold": 0.7,
                "include_raw_text": False,
                "mask_sensitive": True,
            }
        }


class JobStatusRequest(BaseModel):
    """Request schema for querying job status.

    This is typically used as a path parameter, but included
    here for completeness.
    """

    job_id: str = Field(
        ...,
        description="Unique job identifier",
        min_length=1,
    )


class ResultRequest(BaseModel):
    """Request schema for retrieving extraction results.

    This is typically used as a path parameter.
    """

    result_id: str = Field(
        ...,
        description="Unique result identifier",
        min_length=1,
    )


class FilterRequest(BaseModel):
    """Request schema for filtering results."""

    issuer: Optional[IssuerType] = Field(
        default=None,
        description="Filter by issuer",
    )
    min_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score",
    )
    from_date: Optional[str] = Field(
        default=None,
        description="Filter results from this date (ISO format)",
    )
    to_date: Optional[str] = Field(
        default=None,
        description="Filter results to this date (ISO format)",
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of results to return",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of results to skip",
    )

    @field_validator("from_date", "to_date")
    @classmethod
    def validate_date(cls, v: Optional[str]) -> Optional[str]:
        """Validate date format.

        Args:
            v: Date string

        Returns:
            Validated date string

        Raises:
            ValueError: If date format is invalid
        """
        if v is None:
            return v

        # Basic ISO format validation
        from datetime import datetime

        try:
            datetime.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid date format: {v}. Use ISO format (YYYY-MM-DD)")


class RetryJobRequest(BaseModel):
    """Request schema for retrying a failed job."""

    job_id: str = Field(
        ...,
        description="Job ID to retry",
        min_length=1,
    )
    force_ocr: bool = Field(
        default=False,
        description="Force OCR processing on retry",
    )


class CancelJobRequest(BaseModel):
    """Request schema for canceling a running job."""

    job_id: str = Field(
        ...,
        description="Job ID to cancel",
        min_length=1,
    )


class BulkParseRequest(BaseModel):
    """Request schema for parsing multiple documents."""

    document_ids: list[str] = Field(
        ...,
        description="List of document IDs to parse",
        min_length=1,
        max_length=10,
    )
    force_ocr: bool = Field(
        default=False,
        description="Force OCR processing for all documents",
    )
    confidence_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold",
    )

    @field_validator("document_ids")
    @classmethod
    def validate_document_ids(cls, v: list[str]) -> list[str]:
        """Validate document IDs.

        Args:
            v: List of document IDs

        Returns:
            Validated list

        Raises:
            ValueError: If any ID is empty
        """
        if any(not doc_id.strip() for doc_id in v):
            raise ValueError("Document IDs cannot be empty")
        return v


class HealthCheckRequest(BaseModel):
    """Request schema for health check endpoint."""

    detailed: bool = Field(
        default=False,
        description="Include detailed system information",
    )
