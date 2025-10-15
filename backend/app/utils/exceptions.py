"""Custom exception classes for the CC statement parser.

This module defines all custom exceptions used throughout the application
for better error handling and clarity.
"""


class CCParserError(Exception):
    """Base exception class for all CC parser errors."""

    def __init__(self, message: str, details: dict = None):
        """Initialize the exception.

        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ParsingError(CCParserError):
    """Raised when PDF parsing fails.

    This exception is raised when the parser cannot extract text or data
    from the PDF document.
    """

    pass


class ValidationError(CCParserError):
    """Raised when input validation fails.

    This exception is raised when request data, file format, or extracted
    data does not meet validation requirements.
    """

    pass


class OCRError(CCParserError):
    """Raised when OCR processing fails.

    This exception is raised when optical character recognition fails
    or produces unreliable results.
    """

    pass


class FileError(CCParserError):
    """Raised when file operations fail.

    This exception is raised for file-related errors such as:
    - Invalid file format
    - File too large
    - File not found
    - Permission errors
    """

    pass


class ExtractionError(CCParserError):
    """Raised when data extraction fails.

    This exception is raised when the extractor cannot identify or extract
    required fields from the statement.
    """

    pass


class StorageError(CCParserError):
    """Raised when storage operations fail.

    This exception is raised for errors related to file storage,
    whether local filesystem or cloud storage.
    """

    pass


class DatabaseError(CCParserError):
    """Raised when database operations fail.

    This exception is raised for errors related to database operations
    such as connection failures, query errors, or constraint violations.
    """

    pass


class ConfigurationError(CCParserError):
    """Raised when configuration is invalid.

    This exception is raised when application configuration is missing
    or contains invalid values.
    """

    pass


class ProcessingError(CCParserError):
    """Raised when processing pipeline fails.

    This exception is raised for general processing errors that don't
    fit into more specific categories.
    """

    pass


class SecurityError(CCParserError):
    """Raised when security checks fail.

    This exception is raised for security-related issues such as:
    - Suspicious file content
    - Failed encryption/decryption
    - Access violations
    """

    pass


class TimeoutError(CCParserError):
    """Raised when an operation times out.

    This exception is raised when processing takes longer than
    the configured timeout period.
    """

    pass


class IssuerNotSupportedError(CCParserError):
    """Raised when the credit card issuer is not supported.

    This exception is raised when the parser cannot identify the issuer
    or the issuer's statement format is not yet supported.
    """

    pass


class ConfidenceThresholdError(CCParserError):
    """Raised when extraction confidence is below threshold.

    This exception is raised when the confidence score of extracted
    fields is too low to be reliable.
    """

    pass
