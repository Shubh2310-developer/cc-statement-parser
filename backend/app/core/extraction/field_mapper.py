"""Field mapping module for coordinating extraction across modules.

This module coordinates the extraction of specific fields from credit card statements
by integrating text extraction, OCR, layout analysis, and table extraction.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from app.config import get_settings
from app.core.extraction.text_extractor import TextExtractor, ExtractedText
from app.core.extraction.ocr_engine import OCREngine, OCRPageResult
from app.core.extraction.table_extractor import TableExtractor, TransactionRow
from app.core.extraction.layout_analyzer import LayoutAnalyzer, FieldLocation

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ExtractedField:
    """Represents a single extracted field."""

    field_name: str
    value: Optional[str] = None
    confidence: float = 0.0
    source: str = "unknown"  # 'text', 'ocr', 'layout', 'table'
    page_num: Optional[int] = None
    bbox: Optional[tuple] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StatementFields:
    """Collection of extracted statement fields."""

    # Card information
    card_number: Optional[str] = None
    card_holder: Optional[str] = None

    # Statement dates
    statement_date: Optional[str] = None
    due_date: Optional[str] = None
    billing_period_start: Optional[str] = None
    billing_period_end: Optional[str] = None

    # Amounts
    opening_balance: Optional[Decimal] = None
    closing_balance: Optional[Decimal] = None
    total_due: Optional[Decimal] = None
    minimum_due: Optional[Decimal] = None
    credit_limit: Optional[Decimal] = None
    available_credit: Optional[Decimal] = None

    # Transactions
    transactions: List[TransactionRow] = field(default_factory=list)

    # Additional fields
    bank_name: Optional[str] = None
    statement_number: Optional[str] = None

    # Field metadata
    field_confidences: Dict[str, float] = field(default_factory=dict)
    extraction_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'card_number': self.card_number,
            'card_holder': self.card_holder,
            'statement_date': self.statement_date,
            'due_date': self.due_date,
            'billing_period_start': self.billing_period_start,
            'billing_period_end': self.billing_period_end,
            'opening_balance': float(self.opening_balance) if self.opening_balance else None,
            'closing_balance': float(self.closing_balance) if self.closing_balance else None,
            'total_due': float(self.total_due) if self.total_due else None,
            'minimum_due': float(self.minimum_due) if self.minimum_due else None,
            'credit_limit': float(self.credit_limit) if self.credit_limit else None,
            'available_credit': float(self.available_credit) if self.available_credit else None,
            'bank_name': self.bank_name,
            'statement_number': self.statement_number,
            'transactions': [t.to_dict() for t in self.transactions],
            'field_confidences': self.field_confidences,
            'metadata': self.extraction_metadata
        }


class FieldMapper:
    """Coordinate field extraction across different extraction modules."""

    def __init__(self):
        """Initialize field mapper."""
        self.settings = get_settings()
        self.text_extractor = TextExtractor()
        self.ocr_engine = OCREngine()
        self.table_extractor = TableExtractor()
        self.layout_analyzer = LayoutAnalyzer()

    def extract_fields(self, pdf_bytes: bytes) -> StatementFields:
        """Extract all fields from a PDF statement.

        Args:
            pdf_bytes: PDF file content as bytes

        Returns:
            StatementFields object with extracted data

        Raises:
            ValueError: If extraction fails
        """
        logger.info(f"Starting field extraction from PDF bytes")

        try:
            # Step 1: Extract text
            logger.info("Step 1: Extracting text")
            extracted_text = self.text_extractor.extract(pdf_bytes)

            # Step 2: Run OCR if needed
            ocr_results = []
            if extracted_text.is_scanned:
                logger.info("Step 2: Running OCR (scanned document detected)")
                ocr_results = self.ocr_engine.extract_text_from_pdf(pdf_bytes)
            else:
                logger.info("Step 2: Skipping OCR (text-based PDF)")

            # Step 3: Analyze layout
            logger.info("Step 3: Analyzing layout")
            layout_analysis = self.layout_analyzer.analyze_layout(extracted_text)

            # Step 4: Extract tables
            logger.info("Step 4: Extracting tables")
            table_result = self.table_extractor.extract_tables(pdf_bytes)

            # Step 5: Map fields
            logger.info("Step 5: Mapping fields")
            statement_fields = self._map_fields(
                extracted_text,
                ocr_results,
                layout_analysis,
                table_result
            )

            # Add metadata
            statement_fields.extraction_metadata = {
                'file_name': 'uploaded.pdf',
                'total_pages': extracted_text.total_pages,
                'is_scanned': extracted_text.is_scanned,
                'extraction_timestamp': datetime.now().isoformat(),
                'ocr_used': len(ocr_results) > 0,
                'tables_found': len(table_result.tables),
                'transactions_extracted': len(statement_fields.transactions)
            }

            logger.info(
                f"Field extraction complete: "
                f"{len(statement_fields.transactions)} transactions, "
                f"{sum(1 for v in statement_fields.__dict__.values() if v is not None)} fields"
            )

            return statement_fields

        except Exception as e:
            logger.error(f"Field extraction failed: {e}")
            raise ValueError(f"Failed to extract fields: {e}")

    def _map_fields(
        self,
        extracted_text: ExtractedText,
        ocr_results: List[OCRPageResult],
        layout_analysis: Any,
        table_result: Any
    ) -> StatementFields:
        """Map extracted data to statement fields.

        Args:
            extracted_text: ExtractedText object
            ocr_results: List of OCR results
            layout_analysis: LayoutAnalysisResult object
            table_result: TableExtractionResult object

        Returns:
            StatementFields object
        """
        fields = StatementFields()

        # Extract from layout analysis
        self._extract_from_layout(fields, layout_analysis)

        # Extract from text
        full_text = extracted_text.get_full_text()
        self._extract_from_text(fields, full_text)

        # Extract from OCR if available
        if ocr_results:
            ocr_text = "\n\n".join([r.text for r in ocr_results])
            self._extract_from_text(fields, ocr_text)

        # Extract transactions from tables
        if table_result.success:
            for table in table_result.tables:
                fields.transactions.extend(table.rows)

        return fields

    def _extract_from_layout(
        self,
        fields: StatementFields,
        layout_analysis: Any
    ) -> None:
        """Extract fields from layout analysis.

        Args:
            fields: StatementFields object to populate
            layout_analysis: LayoutAnalysisResult object
        """
        for field_location in layout_analysis.field_locations:
            field_name = field_location.label
            value = field_location.value
            confidence = field_location.confidence

            # Map to appropriate field
            if field_name == 'card_number':
                fields.card_number = self._clean_card_number(value)
                fields.field_confidences['card_number'] = confidence

            elif field_name == 'card_holder':
                fields.card_holder = value.strip()
                fields.field_confidences['card_holder'] = confidence

            elif field_name == 'statement_date':
                fields.statement_date = value.strip()
                fields.field_confidences['statement_date'] = confidence

            elif field_name == 'due_date':
                fields.due_date = value.strip()
                fields.field_confidences['due_date'] = confidence

            elif field_name == 'minimum_due':
                fields.minimum_due = self._parse_amount(value)
                fields.field_confidences['minimum_due'] = confidence

            elif field_name == 'total_due':
                fields.total_due = self._parse_amount(value)
                fields.field_confidences['total_due'] = confidence

            elif field_name == 'credit_limit':
                fields.credit_limit = self._parse_amount(value)
                fields.field_confidences['credit_limit'] = confidence

            elif field_name == 'opening_balance':
                fields.opening_balance = self._parse_amount(value)
                fields.field_confidences['opening_balance'] = confidence

            elif field_name == 'closing_balance':
                fields.closing_balance = self._parse_amount(value)
                fields.field_confidences['closing_balance'] = confidence

    def _extract_from_text(
        self,
        fields: StatementFields,
        text: str
    ) -> None:
        """Extract fields from raw text using patterns.

        Args:
            fields: StatementFields object to populate
            text: Text to extract from
        """
        import re

        # Bank name detection
        bank_patterns = [
            r'(HDFC|ICICI|SBI|Axis|American Express|AMEX|Citibank|Standard Chartered)',
        ]
        for pattern in bank_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not fields.bank_name:
                fields.bank_name = match.group(1)
                break

        # Statement number
        stmt_num_patterns = [
            r'Statement\s*(?:Number|No|#)[\s:]*([A-Z0-9]+)',
            r'Statement[\s:]*([A-Z0-9]{8,})'
        ]
        for pattern in stmt_num_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not fields.statement_number:
                fields.statement_number = match.group(1)
                break

        # Available credit (if not already found)
        if not fields.available_credit:
            avail_patterns = [
                r'Available\s*Credit[\s:]*(?:Rs\.?|INR|�)?\s*([0-9,]+\.?\d*)',
                r'Credit\s*Available[\s:]*(?:Rs\.?|INR|�)?\s*([0-9,]+\.?\d*)'
            ]
            for pattern in avail_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    fields.available_credit = self._parse_amount(match.group(1))
                    break

        # Billing period
        period_patterns = [
            r'Billing\s*Period[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*(?:to|-)?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Statement\s*Period[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*(?:to|-)?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        ]
        for pattern in period_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if not fields.billing_period_start:
                    fields.billing_period_start = match.group(1)
                if not fields.billing_period_end:
                    fields.billing_period_end = match.group(2)
                break

    def _clean_card_number(self, card_number: str) -> str:
        """Clean and format card number.

        Args:
            card_number: Raw card number string

        Returns:
            Cleaned card number
        """
        # Remove non-digits except X (for masked digits)
        cleaned = ''.join(c for c in card_number if c.isdigit() or c.upper() == 'X')

        # Mask if configured
        if self.settings.MASK_CARD_NUMBERS and len(cleaned) >= 12:
            # Show only last 4 digits
            cleaned = 'X' * (len(cleaned) - 4) + cleaned[-4:]

        return cleaned

    def _parse_amount(self, amount_str: str) -> Optional[Decimal]:
        """Parse amount string to Decimal.

        Args:
            amount_str: Amount string

        Returns:
            Decimal amount or None
        """
        if not amount_str:
            return None

        try:
            # Remove currency symbols and whitespace
            cleaned = amount_str.replace('\u20b9', '').replace('Rs', '').replace('INR', '')
            cleaned = cleaned.replace('$', '').replace(',', '').strip()

            # Handle negative amounts
            is_negative = False
            if '(' in cleaned and ')' in cleaned:
                is_negative = True
                cleaned = cleaned.replace('(', '').replace(')', '')
            elif cleaned.startswith('-'):
                is_negative = True
                cleaned = cleaned[1:]

            # Parse to Decimal
            amount = Decimal(cleaned)

            if is_negative:
                amount = -amount

            return amount

        except Exception as e:
            logger.debug(f"Could not parse amount '{amount_str}': {e}")
            return None

    def extract_specific_field(
        self,
        pdf_path: Path,
        field_name: str
    ) -> Optional[ExtractedField]:
        """Extract a specific field from PDF.

        Args:
            pdf_path: Path to PDF file
            field_name: Name of field to extract

        Returns:
            ExtractedField object or None
        """
        try:
            # Run full extraction
            fields = self.extract_fields(pdf_path)

            # Get requested field value
            value = getattr(fields, field_name, None)
            if value is None:
                return None

            confidence = fields.field_confidences.get(field_name, 0.0)

            return ExtractedField(
                field_name=field_name,
                value=str(value),
                confidence=confidence,
                source='field_mapper'
            )

        except Exception as e:
            logger.error(f"Failed to extract field '{field_name}': {e}")
            return None

    def validate_extraction(
        self,
        fields: StatementFields
    ) -> Dict[str, Any]:
        """Validate extracted fields.

        Args:
            fields: StatementFields object

        Returns:
            Dictionary with validation results
        """
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'completeness': 0.0
        }

        # Required fields
        required_fields = [
            'card_number', 'statement_date', 'total_due', 'minimum_due'
        ]

        missing_required = []
        for field_name in required_fields:
            if not getattr(fields, field_name):
                missing_required.append(field_name)
                validation['errors'].append(f"Missing required field: {field_name}")

        if missing_required:
            validation['is_valid'] = False

        # Check for low confidence
        for field_name, confidence in fields.field_confidences.items():
            if confidence < self.settings.CONFIDENCE_THRESHOLD:
                validation['warnings'].append(
                    f"Low confidence for field '{field_name}': {confidence:.2f}"
                )

        # Check transactions
        if not fields.transactions:
            validation['warnings'].append("No transactions extracted")

        # Calculate completeness
        total_fields = 13  # Number of main fields
        filled_fields = sum([
            bool(fields.card_number),
            bool(fields.card_holder),
            bool(fields.statement_date),
            bool(fields.due_date),
            bool(fields.billing_period_start),
            bool(fields.billing_period_end),
            bool(fields.opening_balance),
            bool(fields.closing_balance),
            bool(fields.total_due),
            bool(fields.minimum_due),
            bool(fields.credit_limit),
            bool(fields.bank_name),
            bool(fields.transactions)
        ])
        validation['completeness'] = filled_fields / total_fields

        return validation
