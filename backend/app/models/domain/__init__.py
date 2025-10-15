"""Domain models for the CC statement parser."""

from .document import Document
from .extraction_result import ExtractionResult
from .field import BoundingBox, Field
from .job import Job

__all__ = [
    "Field",
    "BoundingBox",
    "Document",
    "Job",
    "ExtractionResult",
]
