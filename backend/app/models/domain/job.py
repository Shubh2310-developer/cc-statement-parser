"""Job domain model.

This module defines the Job model representing a parsing job
that tracks the status and progress of statement processing.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..enums import ErrorCode, JobStatus


@dataclass
class Job:
    """Represents a credit card statement parsing job.

    Attributes:
        id: Unique job identifier
        document_id: ID of the associated document
        status: Current status of the job
        created_at: Timestamp when the job was created
        started_at: Timestamp when processing started
        completed_at: Timestamp when processing completed
        error_message: Error message if job failed
        error_code: Error code if job failed
        result_id: ID of the extraction result (when completed)
        progress: Progress percentage (0-100)
        metadata: Additional job metadata
    """

    status: JobStatus = JobStatus.PENDING
    id: str = field(default_factory=lambda: str(__import__('uuid').uuid4()))
    document_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    error_code: Optional[ErrorCode] = None
    result_id: Optional[str] = None
    progress: int = 0
    metadata: dict = field(default_factory=dict)

    @property
    def is_terminal(self) -> bool:
        """Check if job is in a terminal state.

        Returns:
            True if job is completed or failed
        """
        return JobStatus.is_terminal(self.status)

    @property
    def is_active(self) -> bool:
        """Check if job is in an active state.

        Returns:
            True if job is pending or processing
        """
        return JobStatus.is_active(self.status)

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate job duration in seconds.

        Returns:
            Duration in seconds if started, None otherwise
        """
        if self.started_at is None:
            return None

        end_time = self.completed_at or datetime.utcnow()
        duration = end_time - self.started_at
        return duration.total_seconds()

    @property
    def has_error(self) -> bool:
        """Check if job has an error.

        Returns:
            True if error_message or error_code is set
        """
        return self.error_message is not None or self.error_code is not None

    def start(self) -> "Job":
        """Mark job as started.

        Returns:
            Updated Job instance
        """
        self.status = JobStatus.PROCESSING
        self.started_at = datetime.utcnow()
        self.progress = 0
        return self

    def complete(self, result_id: str) -> "Job":
        """Mark job as completed successfully.

        Args:
            result_id: ID of the extraction result

        Returns:
            Updated Job instance
        """
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.result_id = result_id
        self.progress = 100
        return self

    def fail(
        self,
        error_message: str,
        error_code: Optional[ErrorCode] = None,
    ) -> "Job":
        """Mark job as failed.

        Args:
            error_message: Description of the error
            error_code: Error code

        Returns:
            Updated Job instance
        """
        self.status = JobStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
        self.error_code = error_code or ErrorCode.INTERNAL_ERROR
        return self

    def update_progress(self, progress: int) -> "Job":
        """Update job progress.

        Args:
            progress: Progress percentage (0-100)

        Returns:
            Updated Job instance
        """
        self.progress = max(0, min(100, progress))
        return self

    def add_metadata(self, key: str, value) -> "Job":
        """Add metadata to the job.

        Args:
            key: Metadata key
            value: Metadata value

        Returns:
            Updated Job instance
        """
        self.metadata[key] = value
        return self

    def to_dict(self) -> dict:
        """Convert job to dictionary.

        Returns:
            Dictionary representation of the job
        """
        return {
            "id": self.id,
            "document_id": self.document_id,
            "status": str(self.status),
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "error_code": str(self.error_code) if self.error_code else None,
            "result_id": self.result_id,
            "progress": self.progress,
            "duration_seconds": self.duration_seconds,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Job":
        """Create job from dictionary.

        Args:
            data: Dictionary containing job data

        Returns:
            Job instance
        """
        # Convert string enums back to enum types
        status = data.get("status", JobStatus.PENDING)
        if isinstance(status, str):
            status = JobStatus(status)

        error_code = data.get("error_code")
        if isinstance(error_code, str):
            error_code = ErrorCode(error_code)

        # Parse datetimes
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.utcnow()

        started_at = data.get("started_at")
        if isinstance(started_at, str):
            started_at = datetime.fromisoformat(started_at)

        completed_at = data.get("completed_at")
        if isinstance(completed_at, str):
            completed_at = datetime.fromisoformat(completed_at)

        return cls(
            id=data["id"],
            document_id=data["document_id"],
            status=status,
            created_at=created_at,
            started_at=started_at,
            completed_at=completed_at,
            error_message=data.get("error_message"),
            error_code=error_code,
            result_id=data.get("result_id"),
            progress=data.get("progress", 0),
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        """String representation of the job.

        Returns:
            String representation
        """
        return (
            f"Job(id={self.id}, "
            f"status={self.status}, "
            f"progress={self.progress}%)"
        )
