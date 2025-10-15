"""Document domain model.

This module defines the Document model representing an uploaded
credit card statement PDF file with its metadata.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..enums import DocumentType, IssuerType


@dataclass
class Document:
    """Represents a credit card statement document.

    Attributes:
        id: Unique document identifier
        filename: Original filename
        file_path: Path to the stored file
        file_size: Size of the file in bytes
        file_hash: SHA256 hash of the file
        content_type: MIME type of the file
        page_count: Number of pages in the PDF
        has_text: Whether the PDF has extractable text
        is_scanned: Whether the PDF appears to be scanned
        document_type: Type of document (statement, transaction history, etc.)
        issuer: Detected credit card issuer
        uploaded_at: Timestamp when the document was uploaded
        metadata: Additional document metadata
    """

    id: str
    filename: str
    file_path: str
    file_size: int
    uploaded_at: datetime = field(default_factory=datetime.utcnow)
    file_hash: Optional[str] = None
    content_type: str = "application/pdf"
    page_count: int = 0
    has_text: bool = False
    is_scanned: bool = False
    document_type: DocumentType = DocumentType.UNKNOWN
    issuer: IssuerType = IssuerType.UNKNOWN
    metadata: dict = field(default_factory=dict)

    @property
    def file_size_mb(self) -> float:
        """Get file size in megabytes.

        Returns:
            File size in MB
        """
        return self.file_size / (1024 * 1024)

    @property
    def storage_path(self) -> Path:
        """Get Path object for the file location.

        Returns:
            Path object
        """
        return Path(self.file_path)

    @property
    def requires_ocr(self) -> bool:
        """Check if document requires OCR processing.

        Returns:
            True if OCR is needed, False otherwise
        """
        return self.is_scanned or not self.has_text

    def to_dict(self) -> dict:
        """Convert document to dictionary.

        Returns:
            Dictionary representation of the document
        """
        return {
            "id": self.id,
            "filename": self.filename,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "file_size_mb": round(self.file_size_mb, 2),
            "file_hash": self.file_hash,
            "content_type": self.content_type,
            "page_count": self.page_count,
            "has_text": self.has_text,
            "is_scanned": self.is_scanned,
            "document_type": str(self.document_type),
            "issuer": str(self.issuer),
            "uploaded_at": self.uploaded_at.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Document":
        """Create document from dictionary.

        Args:
            data: Dictionary containing document data

        Returns:
            Document instance
        """
        # Convert string enums back to enum types
        document_type = data.get("document_type", DocumentType.UNKNOWN)
        if isinstance(document_type, str):
            document_type = DocumentType(document_type)

        issuer = data.get("issuer", IssuerType.UNKNOWN)
        if isinstance(issuer, str):
            issuer = IssuerType(issuer)

        # Parse datetime
        uploaded_at = data.get("uploaded_at")
        if isinstance(uploaded_at, str):
            uploaded_at = datetime.fromisoformat(uploaded_at)
        elif uploaded_at is None:
            uploaded_at = datetime.utcnow()

        return cls(
            id=data["id"],
            filename=data["filename"],
            file_path=data["file_path"],
            file_size=data["file_size"],
            file_hash=data.get("file_hash"),
            content_type=data.get("content_type", "application/pdf"),
            page_count=data.get("page_count", 0),
            has_text=data.get("has_text", False),
            is_scanned=data.get("is_scanned", False),
            document_type=document_type,
            issuer=issuer,
            uploaded_at=uploaded_at,
            metadata=data.get("metadata", {}),
        )

    def update_from_validation(
        self,
        page_count: int,
        has_text: bool,
        file_hash: str,
    ) -> "Document":
        """Update document with validation results.

        Args:
            page_count: Number of pages
            has_text: Whether PDF has extractable text
            file_hash: File hash

        Returns:
            Updated Document instance
        """
        self.page_count = page_count
        self.has_text = has_text
        self.is_scanned = not has_text
        self.file_hash = file_hash
        return self

    def set_issuer(self, issuer: IssuerType) -> "Document":
        """Set the document issuer.

        Args:
            issuer: Detected issuer

        Returns:
            Updated Document instance
        """
        self.issuer = issuer
        return self

    def set_document_type(self, document_type: DocumentType) -> "Document":
        """Set the document type.

        Args:
            document_type: Type of document

        Returns:
            Updated Document instance
        """
        self.document_type = document_type
        return self

    def add_metadata(self, key: str, value) -> "Document":
        """Add metadata to the document.

        Args:
            key: Metadata key
            value: Metadata value

        Returns:
            Updated Document instance
        """
        self.metadata[key] = value
        return self

    def __repr__(self) -> str:
        """String representation of the document.

        Returns:
            String representation
        """
        return (
            f"Document(id={self.id}, "
            f"filename={self.filename}, "
            f"issuer={self.issuer}, "
            f"pages={self.page_count})"
        )
