"""Document ingestion and validation."""
import uuid
from pathlib import Path
from datetime import datetime

from app.models.domain.document import Document
from app.utils.file_utils import validate_pdf_file, get_file_hash, is_pdf_scanned
from app.utils.logger import get_logger
from app.utils.exceptions import FileError

logger = get_logger(__name__)


class DocumentIngestion:
    """Handle document upload and validation."""

    def ingest_file(self, file_bytes: bytes, filename: str) -> Document:
        """
        Ingest and validate uploaded file.

        Args:
            file_bytes: File content
            filename: Original filename

        Returns:
            Document domain model

        Raises:
            FileError: If validation fails
        """
        logger.info(f"Ingesting file: {filename}")

        # Validate PDF using PyMuPDF directly
        try:
            # Import PyMuPDF - avoid conflict with frontend directory
            try:
                import pymupdf as fitz
            except ImportError:
                import fitz
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            if doc.is_encrypted:
                doc.close()
                raise FileError("PDF is encrypted")
            doc.close()
        except Exception as e:
            raise FileError(f"Invalid PDF: {str(e)}")

        # Calculate hash
        import hashlib
        file_hash = hashlib.sha256(file_bytes).hexdigest()

        # Check if scanned
        is_scanned = is_pdf_scanned(file_bytes)

        # Create document
        document = Document(
            id=str(uuid.uuid4()),
            filename=filename,
            file_path="",  # Will be set after storage
            file_hash=file_hash,
            file_size=len(file_bytes),
            uploaded_at=datetime.utcnow(),
            is_scanned=is_scanned
        )

        logger.info(f"Document ingested: {document.id}")
        return document
