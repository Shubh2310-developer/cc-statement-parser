"""Internal DTOs (Data Transfer Objects).

This module defines internal data structures used for
communication between different layers of the application.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from ..enums import ExtractionMethod, IssuerType


@dataclass
class PDFMetadata:
    """Internal DTO for PDF metadata."""

    page_count: int
    has_text: bool
    file_hash: str
    is_encrypted: bool = False
    pdf_version: Optional[str] = None
    author: Optional[str] = None
    title: Optional[str] = None
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None


@dataclass
class TextExtractionResult:
    """Internal DTO for text extraction results."""

    text: str
    method: ExtractionMethod
    page_texts: dict[int, str] = field(default_factory=dict)
    confidence: float = 1.0
    metadata: dict = field(default_factory=dict)


@dataclass
class OCRResult:
    """Internal DTO for OCR processing results."""

    text: str
    confidence: float
    language: str = "eng"
    processing_time: float = 0.0
    page_results: dict[int, dict] = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


@dataclass
class IssuerDetectionResult:
    """Internal DTO for issuer detection results."""

    issuer: IssuerType
    confidence: float
    detection_method: str
    patterns_matched: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class FieldExtractionContext:
    """Internal DTO for field extraction context."""

    document_id: str
    issuer: IssuerType
    raw_text: str
    page_texts: dict[int, str] = field(default_factory=dict)
    force_ocr: bool = False
    confidence_threshold: float = 0.7
    metadata: dict = field(default_factory=dict)


@dataclass
class ExtractionMetrics:
    """Internal DTO for extraction metrics."""

    total_fields_attempted: int = 0
    fields_extracted: int = 0
    fields_failed: int = 0
    average_confidence: float = 0.0
    processing_time_seconds: float = 0.0
    ocr_used: bool = False
    extraction_method: Optional[ExtractionMethod] = None
    errors: list[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Internal DTO for validation results."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class ProcessingOptions:
    """Internal DTO for processing options."""

    force_ocr: bool = False
    confidence_threshold: float = 0.7
    include_raw_text: bool = False
    mask_sensitive: bool = True
    issuer_hint: Optional[IssuerType] = None
    timeout_seconds: int = 60
    enable_caching: bool = True


@dataclass
class StorageLocation:
    """Internal DTO for storage locations."""

    storage_type: str  # 'local' or 's3'
    path: str
    bucket: Optional[str] = None
    region: Optional[str] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class CacheEntry:
    """Internal DTO for cache entries."""

    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)

    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired.

        Returns:
            True if expired, False otherwise
        """
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at


@dataclass
class ProcessingStep:
    """Internal DTO for tracking processing steps."""

    name: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate step duration.

        Returns:
            Duration in seconds if started, None otherwise
        """
        if self.started_at is None:
            return None
        end_time = self.completed_at or datetime.utcnow()
        return (end_time - self.started_at).total_seconds()


@dataclass
class ProcessingPipeline:
    """Internal DTO for tracking a processing pipeline."""

    id: str
    document_id: str
    steps: list[ProcessingStep] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)

    def add_step(self, name: str) -> ProcessingStep:
        """Add a new step to the pipeline.

        Args:
            name: Step name

        Returns:
            Created ProcessingStep
        """
        step = ProcessingStep(name=name, status="pending")
        self.steps.append(step)
        return step

    @property
    def current_step(self) -> Optional[ProcessingStep]:
        """Get the currently running step.

        Returns:
            Current step or None
        """
        for step in self.steps:
            if step.status == "running":
                return step
        return None

    @property
    def total_duration_seconds(self) -> Optional[float]:
        """Calculate total pipeline duration.

        Returns:
            Duration in seconds
        """
        end_time = self.completed_at or datetime.utcnow()
        return (end_time - self.started_at).total_seconds()


@dataclass
class TableExtractionResult:
    """Internal DTO for table extraction results."""

    tables: list[dict] = field(default_factory=list)
    method: str = "camelot"
    confidence: float = 0.0
    metadata: dict = field(default_factory=dict)


@dataclass
class PatternMatch:
    """Internal DTO for pattern matching results."""

    pattern: str
    match: str
    start: int
    end: int
    groups: tuple = field(default_factory=tuple)
    metadata: dict = field(default_factory=dict)


@dataclass
class ExtractionAttempt:
    """Internal DTO for tracking field extraction attempts."""

    field_type: str
    success: bool
    value: Any = None
    confidence: float = 0.0
    method: Optional[str] = None
    error: Optional[str] = None
    attempts: int = 1
    metadata: dict = field(default_factory=dict)


@dataclass
class BatchProcessingJob:
    """Internal DTO for batch processing jobs."""

    batch_id: str
    document_ids: list[str]
    total: int
    completed: int = 0
    failed: int = 0
    job_ids: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)

    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage.

        Returns:
            Progress as percentage (0-100)
        """
        if self.total == 0:
            return 0.0
        processed = self.completed + self.failed
        return (processed / self.total) * 100


@dataclass
class SystemMetrics:
    """Internal DTO for system metrics."""

    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_jobs: int
    queue_size: int
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)
