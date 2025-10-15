"""Response Pydantic schemas.

This module defines Pydantic models for API responses
that match frontend expectations.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from ..enums import DocumentType, ErrorCode, IssuerType, JobStatus


class FieldResponse(BaseModel):
    """Response schema for an extracted field."""

    field_type: str = Field(..., description="Type of the field")
    value: Any = Field(..., description="Extracted value")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")
    raw_value: Optional[str] = Field(None, description="Original raw value")
    snippet: Optional[str] = Field(None, description="Text snippet from document")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "field_type": "total_amount_due",
                "value": 12345.67,
                "confidence": 0.95,
                "raw_value": "₹12,345.67",
                "snippet": "Total Amount Due: ₹12,345.67",
            }
        }


class DocumentResponse(BaseModel):
    """Response schema for a document."""

    id: str = Field(..., description="Document ID")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    page_count: int = Field(..., description="Number of pages")
    has_text: bool = Field(..., description="Whether PDF has extractable text")
    is_scanned: bool = Field(..., description="Whether PDF appears to be scanned")
    document_type: str = Field(..., description="Type of document")
    issuer: str = Field(..., description="Detected issuer")
    uploaded_at: str = Field(..., description="Upload timestamp (ISO format)")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "id": "doc_123456",
                "filename": "statement_jan_2024.pdf",
                "file_size": 524288,
                "page_count": 5,
                "has_text": True,
                "is_scanned": False,
                "document_type": "statement",
                "issuer": "hdfc",
                "uploaded_at": "2024-01-15T10:30:00",
            }
        }


class JobResponse(BaseModel):
    """Response schema for a parsing job."""

    id: str = Field(..., description="Job ID")
    document_id: str = Field(..., description="Associated document ID")
    status: str = Field(..., description="Job status")
    progress: int = Field(..., description="Progress percentage (0-100)")
    created_at: str = Field(..., description="Creation timestamp (ISO format)")
    started_at: Optional[str] = Field(None, description="Start timestamp (ISO format)")
    completed_at: Optional[str] = Field(
        None, description="Completion timestamp (ISO format)"
    )
    error_message: Optional[str] = Field(None, description="Error message if failed")
    error_code: Optional[str] = Field(None, description="Error code if failed")
    result_id: Optional[str] = Field(None, description="Result ID when completed")
    duration_seconds: Optional[float] = Field(None, description="Processing duration")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "id": "job_123456",
                "document_id": "doc_123456",
                "status": "completed",
                "progress": 100,
                "created_at": "2024-01-15T10:30:00",
                "started_at": "2024-01-15T10:30:05",
                "completed_at": "2024-01-15T10:30:15",
                "error_message": None,
                "error_code": None,
                "result_id": "result_123456",
                "duration_seconds": 10.5,
            }
        }


class ExtractionResultResponse(BaseModel):
    """Response schema for extraction results."""

    id: str = Field(..., description="Result ID")
    job_id: str = Field(..., description="Associated job ID")
    document_id: str = Field(..., description="Associated document ID")
    issuer: str = Field(..., description="Detected issuer")
    fields: dict[str, FieldResponse] = Field(..., description="Extracted fields")
    confidence_score: float = Field(
        ..., description="Overall confidence score (0.0-1.0)"
    )
    field_count: int = Field(..., description="Number of extracted fields")
    created_at: str = Field(..., description="Creation timestamp (ISO format)")
    raw_text: Optional[str] = Field(None, description="Raw extracted text")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "id": "result_123456",
                "job_id": "job_123456",
                "document_id": "doc_123456",
                "issuer": "hdfc",
                "fields": {
                    "total_amount_due": {
                        "field_type": "total_amount_due",
                        "value": 12345.67,
                        "confidence": 0.95,
                        "raw_value": "₹12,345.67",
                        "snippet": "Total Amount Due: ₹12,345.67",
                    }
                },
                "confidence_score": 0.92,
                "field_count": 15,
                "created_at": "2024-01-15T10:30:15",
                "raw_text": None,
            }
        }


class UploadResponse(BaseModel):
    """Response schema for file upload."""

    document_id: str = Field(..., description="Uploaded document ID")
    job_id: str = Field(..., description="Created job ID")
    message: str = Field(..., description="Success message")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "document_id": "doc_123456",
                "job_id": "job_123456",
                "message": "File uploaded successfully and processing started",
            }
        }


class ErrorResponse(BaseModel):
    """Response schema for errors."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    code: Optional[str] = Field(None, description="Error code")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid file format. Only PDF files are supported.",
                "details": {"filename": "document.jpg"},
                "code": "INVALID_FILE_TYPE",
            }
        }


class HealthCheckResponse(BaseModel):
    """Response schema for health check."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp (ISO format)")
    details: Optional[dict] = Field(None, description="Additional system details")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2024-01-15T10:30:00",
                "details": {
                    "database": "connected",
                    "storage": "available",
                    "ocr": "enabled",
                },
            }
        }


class ListJobsResponse(BaseModel):
    """Response schema for listing jobs."""

    jobs: list[JobResponse] = Field(..., description="List of jobs")
    total: int = Field(..., description="Total number of jobs")
    limit: int = Field(..., description="Page size limit")
    offset: int = Field(..., description="Offset for pagination")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "jobs": [
                    {
                        "id": "job_123456",
                        "document_id": "doc_123456",
                        "status": "completed",
                        "progress": 100,
                        "created_at": "2024-01-15T10:30:00",
                        "result_id": "result_123456",
                    }
                ],
                "total": 50,
                "limit": 10,
                "offset": 0,
            }
        }


class ListResultsResponse(BaseModel):
    """Response schema for listing results."""

    results: list[ExtractionResultResponse] = Field(
        ..., description="List of extraction results"
    )
    total: int = Field(..., description="Total number of results")
    limit: int = Field(..., description="Page size limit")
    offset: int = Field(..., description="Offset for pagination")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "id": "result_123456",
                        "job_id": "job_123456",
                        "document_id": "doc_123456",
                        "issuer": "hdfc",
                        "fields": {},
                        "confidence_score": 0.92,
                        "field_count": 15,
                        "created_at": "2024-01-15T10:30:15",
                    }
                ],
                "total": 25,
                "limit": 10,
                "offset": 0,
            }
        }


class BulkParseResponse(BaseModel):
    """Response schema for bulk parsing."""

    jobs: list[JobResponse] = Field(..., description="Created jobs")
    total_jobs: int = Field(..., description="Total number of jobs created")
    message: str = Field(..., description="Success message")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "jobs": [
                    {
                        "id": "job_123456",
                        "document_id": "doc_123456",
                        "status": "pending",
                        "progress": 0,
                        "created_at": "2024-01-15T10:30:00",
                    }
                ],
                "total_jobs": 5,
                "message": "5 parsing jobs created successfully",
            }
        }


class StatsResponse(BaseModel):
    """Response schema for statistics."""

    total_documents: int = Field(..., description="Total documents uploaded")
    total_jobs: int = Field(..., description="Total jobs created")
    completed_jobs: int = Field(..., description="Completed jobs")
    failed_jobs: int = Field(..., description="Failed jobs")
    pending_jobs: int = Field(..., description="Pending jobs")
    processing_jobs: int = Field(..., description="Currently processing jobs")
    average_confidence: float = Field(
        ..., description="Average confidence score across all results"
    )
    issuer_breakdown: dict[str, int] = Field(
        ..., description="Breakdown by issuer"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "total_documents": 100,
                "total_jobs": 100,
                "completed_jobs": 85,
                "failed_jobs": 5,
                "pending_jobs": 8,
                "processing_jobs": 2,
                "average_confidence": 0.89,
                "issuer_breakdown": {
                    "hdfc": 30,
                    "icici": 25,
                    "axis": 20,
                    "sbi": 15,
                    "unknown": 10,
                },
            }
        }


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str = Field(..., description="Response message")
    success: bool = Field(default=True, description="Operation success status")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "message": "Operation completed successfully",
                "success": True,
            }
        }
