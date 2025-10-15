"""File utility functions for PDF validation and handling.

This module provides utilities for validating, checking, and managing
uploaded PDF files.
"""

import hashlib
import mimetypes
from pathlib import Path
from typing import BinaryIO, Optional, Union

# Import PyMuPDF - avoid conflict with frontend directory
try:
    import pymupdf as fitz
except ImportError:
    import fitz

from .exceptions import FileError, ValidationError


def validate_file_extension(
    filename: str,
    allowed_extensions: set[str] = {".pdf"},
) -> bool:
    """Validate file extension.

    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed extensions (e.g., {'.pdf', '.jpg'})

    Returns:
        True if extension is allowed, False otherwise
    """
    file_path = Path(filename)
    return file_path.suffix.lower() in allowed_extensions


def validate_file_size(
    file_size: int,
    max_size: int = 10 * 1024 * 1024,  # 10MB default
) -> bool:
    """Validate file size.

    Args:
        file_size: Size of file in bytes
        max_size: Maximum allowed size in bytes

    Returns:
        True if size is within limit, False otherwise
    """
    return 0 < file_size <= max_size


def get_file_hash(file_path: Union[str, Path], algorithm: str = "sha256") -> str:
    """Calculate hash of a file.

    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use (md5, sha1, sha256, etc.)

    Returns:
        Hexadecimal hash string

    Raises:
        FileError: If file cannot be read
    """
    hash_func = hashlib.new(algorithm)

    try:
        with open(file_path, "rb") as f:
            # Read file in chunks to handle large files
            for chunk in iter(lambda: f.read(8192), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        raise FileError(
            f"Failed to calculate file hash: {str(e)}",
            details={"file_path": str(file_path), "algorithm": algorithm},
        )


def validate_pdf_file(file_path: Union[str, Path]) -> dict:
    """Validate that a file is a valid PDF.

    Args:
        file_path: Path to the PDF file

    Returns:
        Dictionary with validation results and PDF metadata

    Raises:
        FileError: If file is not a valid PDF
        ValidationError: If PDF is corrupted or encrypted
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileError(f"File not found: {file_path}")

    if not file_path.is_file():
        raise FileError(f"Not a file: {file_path}")

    # Check extension
    if not validate_file_extension(str(file_path)):
        raise ValidationError(
            f"Invalid file extension. Expected .pdf, got {file_path.suffix}"
        )

    # Check MIME type
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type != "application/pdf":
        raise ValidationError(
            f"Invalid MIME type. Expected application/pdf, got {mime_type}"
        )

    # Try to open with PyMuPDF
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        raise ValidationError(
            f"Failed to open PDF: {str(e)}",
            details={"file_path": str(file_path)},
        )

    try:
        # Check if encrypted
        if doc.is_encrypted:
            doc.close()
            raise ValidationError(
                "PDF is encrypted. Please provide an unencrypted PDF.",
                details={"file_path": str(file_path)},
            )

        # Get metadata
        metadata = {
            "page_count": doc.page_count,
            "is_encrypted": doc.is_encrypted,
            "is_pdf": doc.is_pdf,
            "metadata": doc.metadata,
        }

        # Check if PDF has pages
        if doc.page_count == 0:
            doc.close()
            raise ValidationError(
                "PDF has no pages",
                details={"file_path": str(file_path)},
            )

        doc.close()
        return metadata

    except Exception as e:
        if isinstance(e, (ValidationError, FileError)):
            raise
        raise ValidationError(
            f"PDF validation failed: {str(e)}",
            details={"file_path": str(file_path)},
        )


def get_pdf_page_count(file_path: Union[str, Path]) -> int:
    """Get the number of pages in a PDF.

    Args:
        file_path: Path to the PDF file

    Returns:
        Number of pages

    Raises:
        FileError: If file cannot be read
    """
    try:
        doc = fitz.open(file_path)
        page_count = doc.page_count
        doc.close()
        return page_count
    except Exception as e:
        raise FileError(
            f"Failed to read PDF page count: {str(e)}",
            details={"file_path": str(file_path)},
        )


def check_pdf_has_text(file_path: Union[str, Path], min_text_length: int = 50) -> bool:
    """Check if PDF has extractable text.

    Args:
        file_path: Path to the PDF file
        min_text_length: Minimum text length to consider PDF as having text

    Returns:
        True if PDF has extractable text, False otherwise
    """
    try:
        doc = fitz.open(file_path)
        total_text = ""

        # Check first few pages for text
        pages_to_check = min(3, doc.page_count)
        for page_num in range(pages_to_check):
            page = doc[page_num]
            text = page.get_text()
            total_text += text

            # Early exit if we have enough text
            if len(total_text) >= min_text_length:
                doc.close()
                return True

        doc.close()
        return len(total_text) >= min_text_length

    except Exception:
        # If we can't read text, assume it doesn't have text
        return False


def is_pdf_scanned(file_path: Union[str, Path], text_threshold: int = 100) -> bool:
    """Determine if a PDF is scanned (image-based) or text-based.

    Args:
        file_path: Path to the PDF file
        text_threshold: Minimum text length to consider PDF as text-based

    Returns:
        True if PDF appears to be scanned, False if text-based
    """
    return not check_pdf_has_text(file_path, min_text_length=text_threshold)


def ensure_directory(directory: Union[str, Path]) -> Path:
    """Ensure a directory exists, creating it if necessary.

    Args:
        directory: Path to the directory

    Returns:
        Path object for the directory

    Raises:
        FileError: If directory cannot be created
    """
    dir_path = Path(directory)
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
    except Exception as e:
        raise FileError(
            f"Failed to create directory: {str(e)}",
            details={"directory": str(directory)},
        )


def safe_filename(filename: str) -> str:
    """Generate a safe filename by removing/replacing problematic characters.

    Args:
        filename: Original filename

    Returns:
        Safe filename
    """
    # Replace problematic characters
    safe_chars = "-_.() "
    filename = "".join(
        c if c.isalnum() or c in safe_chars else "_" for c in filename
    )

    # Remove multiple consecutive underscores/spaces
    while "__" in filename:
        filename = filename.replace("__", "_")
    while "  " in filename:
        filename = filename.replace("  ", " ")

    # Strip leading/trailing whitespace and dots
    filename = filename.strip(". ")

    return filename or "unnamed"


def get_unique_filename(directory: Union[str, Path], filename: str) -> Path:
    """Get a unique filename in a directory by adding a counter if needed.

    Args:
        directory: Directory path
        filename: Desired filename

    Returns:
        Path object with unique filename
    """
    dir_path = Path(directory)
    file_path = dir_path / filename

    if not file_path.exists():
        return file_path

    # File exists, add counter
    stem = file_path.stem
    suffix = file_path.suffix
    counter = 1

    while True:
        new_filename = f"{stem}_{counter}{suffix}"
        new_path = dir_path / new_filename
        if not new_path.exists():
            return new_path
        counter += 1


def read_file_chunks(
    file_obj: BinaryIO,
    chunk_size: int = 8192,
):
    """Read file in chunks (generator).

    Args:
        file_obj: File object to read
        chunk_size: Size of each chunk in bytes

    Yields:
        Bytes chunks
    """
    while True:
        chunk = file_obj.read(chunk_size)
        if not chunk:
            break
        yield chunk


def get_file_info(file_path: Union[str, Path]) -> dict:
    """Get comprehensive information about a file.

    Args:
        file_path: Path to the file

    Returns:
        Dictionary with file information

    Raises:
        FileError: If file cannot be accessed
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileError(f"File not found: {file_path}")

    try:
        stat = file_path.stat()
        return {
            "name": file_path.name,
            "size": stat.st_size,
            "extension": file_path.suffix,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "is_file": file_path.is_file(),
            "is_dir": file_path.is_dir(),
            "absolute_path": str(file_path.absolute()),
        }
    except Exception as e:
        raise FileError(
            f"Failed to get file info: {str(e)}",
            details={"file_path": str(file_path)},
        )
