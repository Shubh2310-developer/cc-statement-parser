"""Enumerations for the CC statement parser.

This module defines all enums used throughout the application for
consistent status tracking, issuer identification, and field classification.
"""

from enum import Enum


class JobStatus(str, Enum):
    """Status of a parsing job."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

    def __str__(self) -> str:
        """Return the value as string."""
        return self.value

    @classmethod
    def is_terminal(cls, status: "JobStatus") -> bool:
        """Check if a status is terminal (completed or failed).

        Args:
            status: Job status to check

        Returns:
            True if status is terminal, False otherwise
        """
        return status in (cls.COMPLETED, cls.FAILED)

    @classmethod
    def is_active(cls, status: "JobStatus") -> bool:
        """Check if a status is active (pending or processing).

        Args:
            status: Job status to check

        Returns:
            True if status is active, False otherwise
        """
        return status in (cls.PENDING, cls.PROCESSING)


class IssuerType(str, Enum):
    """Credit card issuer types."""

    HDFC = "hdfc"
    ICICI = "icici"
    AXIS = "axis"
    SBI = "sbi"
    AMEX = "amex"
    CITIBANK = "citibank"
    STANDARD_CHARTERED = "standard_chartered"
    HSBC = "hsbc"
    KOTAK = "kotak"
    YES_BANK = "yes_bank"
    INDUSIND = "indusind"
    RBL = "rbl"
    IDFC_FIRST = "idfc_first"
    AU_BANK = "au_bank"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        """Return the value as string."""
        return self.value

    @property
    def display_name(self) -> str:
        """Get display name for the issuer.

        Returns:
            Human-readable issuer name
        """
        display_names = {
            self.HDFC: "HDFC Bank",
            self.ICICI: "ICICI Bank",
            self.AXIS: "Axis Bank",
            self.SBI: "State Bank of India",
            self.AMEX: "American Express",
            self.CITIBANK: "Citibank",
            self.STANDARD_CHARTERED: "Standard Chartered",
            self.HSBC: "HSBC",
            self.KOTAK: "Kotak Mahindra Bank",
            self.YES_BANK: "Yes Bank",
            self.INDUSIND: "IndusInd Bank",
            self.RBL: "RBL Bank",
            self.IDFC_FIRST: "IDFC FIRST Bank",
            self.AU_BANK: "AU Small Finance Bank",
            self.UNKNOWN: "Unknown",
        }
        return display_names.get(self, self.value)


class FieldType(str, Enum):
    """Types of fields extracted from credit card statements."""

    # Card Information
    CARD_NUMBER = "card_number"
    CARD_LAST_4_DIGITS = "card_last_4_digits"
    CARDHOLDER_NAME = "cardholder_name"
    CARD_TYPE = "card_type"
    CARD_VARIANT = "card_variant"

    # Statement Period
    STATEMENT_DATE = "statement_date"
    STATEMENT_PERIOD_START = "statement_period_start"
    STATEMENT_PERIOD_END = "statement_period_end"

    # Payment Information
    PAYMENT_DUE_DATE = "payment_due_date"
    MINIMUM_AMOUNT_DUE = "minimum_amount_due"
    TOTAL_AMOUNT_DUE = "total_amount_due"

    # Balance Information
    OPENING_BALANCE = "opening_balance"
    CLOSING_BALANCE = "closing_balance"
    CREDIT_LIMIT = "credit_limit"
    AVAILABLE_CREDIT = "available_credit"

    # Amounts
    TOTAL_PURCHASES = "total_purchases"
    TOTAL_PAYMENTS = "total_payments"
    TOTAL_FEES = "total_fees"
    TOTAL_INTEREST = "total_interest"

    # Other
    CUSTOMER_ID = "customer_id"
    STATEMENT_NUMBER = "statement_number"
    REWARD_POINTS = "reward_points"
    ISSUER = "issuer"

    # Metadata
    CURRENCY = "currency"
    CONTACT_NUMBER = "contact_number"
    EMAIL = "email"

    def __str__(self) -> str:
        """Return the value as string."""
        return self.value

    @property
    def display_name(self) -> str:
        """Get display name for the field.

        Returns:
            Human-readable field name
        """
        # Convert snake_case to Title Case
        return self.value.replace("_", " ").title()

    @property
    def is_amount(self) -> bool:
        """Check if field represents a monetary amount.

        Returns:
            True if field is an amount, False otherwise
        """
        amount_fields = {
            self.MINIMUM_AMOUNT_DUE,
            self.TOTAL_AMOUNT_DUE,
            self.OPENING_BALANCE,
            self.CLOSING_BALANCE,
            self.CREDIT_LIMIT,
            self.AVAILABLE_CREDIT,
            self.TOTAL_PURCHASES,
            self.TOTAL_PAYMENTS,
            self.TOTAL_FEES,
            self.TOTAL_INTEREST,
        }
        return self in amount_fields

    @property
    def is_date(self) -> bool:
        """Check if field represents a date.

        Returns:
            True if field is a date, False otherwise
        """
        date_fields = {
            self.STATEMENT_DATE,
            self.STATEMENT_PERIOD_START,
            self.STATEMENT_PERIOD_END,
            self.PAYMENT_DUE_DATE,
        }
        return self in date_fields

    @property
    def is_sensitive(self) -> bool:
        """Check if field contains sensitive information.

        Returns:
            True if field is sensitive, False otherwise
        """
        sensitive_fields = {
            self.CARD_NUMBER,
            self.CARDHOLDER_NAME,
            self.CUSTOMER_ID,
            self.CONTACT_NUMBER,
            self.EMAIL,
        }
        return self in sensitive_fields


class ExtractionMethod(str, Enum):
    """Method used to extract data from PDF."""

    TEXT_EXTRACTION = "text_extraction"
    OCR = "ocr"
    TABLE_EXTRACTION = "table_extraction"
    REGEX = "regex"
    PATTERN_MATCHING = "pattern_matching"
    ML_MODEL = "ml_model"
    HYBRID = "hybrid"

    def __str__(self) -> str:
        """Return the value as string."""
        return self.value


class DocumentType(str, Enum):
    """Type of credit card document."""

    STATEMENT = "statement"
    TRANSACTION_HISTORY = "transaction_history"
    PAYMENT_RECEIPT = "payment_receipt"
    REWARD_SUMMARY = "reward_summary"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        """Return the value as string."""
        return self.value


class TransactionType(str, Enum):
    """Type of credit card transaction."""

    PURCHASE = "purchase"
    PAYMENT = "payment"
    REFUND = "refund"
    FEE = "fee"
    INTEREST = "interest"
    REVERSAL = "reversal"
    CASHBACK = "cashback"
    REWARD_REDEMPTION = "reward_redemption"
    OTHER = "other"

    def __str__(self) -> str:
        """Return the value as string."""
        return self.value


class ErrorCode(str, Enum):
    """Error codes for the application."""

    # File Errors
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    FILE_CORRUPTED = "FILE_CORRUPTED"

    # PDF Errors
    PDF_ENCRYPTED = "PDF_ENCRYPTED"
    PDF_NO_PAGES = "PDF_NO_PAGES"
    PDF_PARSE_ERROR = "PDF_PARSE_ERROR"

    # Extraction Errors
    NO_TEXT_FOUND = "NO_TEXT_FOUND"
    ISSUER_NOT_DETECTED = "ISSUER_NOT_DETECTED"
    EXTRACTION_FAILED = "EXTRACTION_FAILED"
    CONFIDENCE_TOO_LOW = "CONFIDENCE_TOO_LOW"

    # OCR Errors
    OCR_FAILED = "OCR_FAILED"
    OCR_TIMEOUT = "OCR_TIMEOUT"

    # Validation Errors
    VALIDATION_FAILED = "VALIDATION_FAILED"
    INVALID_DATE_FORMAT = "INVALID_DATE_FORMAT"
    INVALID_AMOUNT_FORMAT = "INVALID_AMOUNT_FORMAT"

    # System Errors
    TIMEOUT = "TIMEOUT"
    STORAGE_ERROR = "STORAGE_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"

    def __str__(self) -> str:
        """Return the value as string."""
        return self.value
