"""Base parser interface for credit card statement parsing."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import re
from datetime import datetime

from app.models.enums import IssuerType, FieldType
from app.models.domain.extraction_result import ExtractionResult
from app.models.domain.field import Field, BoundingBox
from app.utils.logger import get_logger
from app.utils.date_parser import parse_date, extract_dates_from_text
from app.utils.currency_parser import parse_currency, extract_amounts_from_text
from app.utils.security import mask_card_number, extract_card_number
from app.utils.exceptions import ParsingError

logger = get_logger(__name__)


class BaseParser(ABC):
    """Abstract base class for all bank-specific parsers."""

    def __init__(self):
        """Initialize parser."""
        self.logger = logger

    @abstractmethod
    def get_issuer_type(self) -> IssuerType:
        """Return the issuer type this parser handles."""
        pass

    @abstractmethod
    def can_parse(self, text: str) -> tuple[bool, float]:
        """
        Check if this parser can handle the given document.
        
        Args:
            text: Full text extracted from PDF
            
        Returns:
            Tuple of (can_parse, confidence_score)
        """
        pass

    @abstractmethod
    def get_patterns(self) -> Dict[str, List[str]]:
        """
        Get bank-specific regex patterns.
        
        Returns:
            Dictionary mapping field names to regex patterns
        """
        pass

    def parse(self, text: str, extracted_fields: Optional[Dict[str, Any]] = None) -> ExtractionResult:
        """
        Parse the statement text and extract all fields.
        
        Args:
            text: Full text from PDF
            extracted_fields: Pre-extracted fields from FieldMapper (optional)
            
        Returns:
            ExtractionResult with all extracted data
        """
        self.logger.info(f"Parsing with {self.__class__.__name__}")

        import uuid
        result = ExtractionResult(
            id=str(uuid.uuid4()),
            job_id="",  # Will be set by service layer
            document_id="",  # Will be set by service layer
            issuer=self.get_issuer_type(),
            raw_text=text[:500]  # Store snippet for debugging
        )
        
        try:
            # Extract card information
            card_info = self.extract_card_info(text)
            if card_info:
                for field_type, field_obj in card_info.items():
                    result.add_field(field_obj)

            # Extract dates
            dates = self.extract_billing_dates(text)
            if dates:
                for field_type, field_obj in dates.items():
                    result.add_field(field_obj)

            # Extract amounts
            amounts = self.extract_balance(text)
            if amounts:
                for field_type, field_obj in amounts.items():
                    result.add_field(field_obj)

            # Extract transactions - skip for now due to field type issues
            # transactions = self.extract_transactions(text)
            
            self.logger.info(f"Successfully extracted {result.field_count} fields")
            
        except Exception as e:
            self.logger.error(f"Parsing error: {e}")
            raise ParsingError(f"Failed to parse {self.get_issuer_type().value} statement", details=str(e))
        
        return result

    def extract_card_info(self, text: str) -> Dict[FieldType, Field]:
        """
        Extract card-related information.
        
        Returns:
            Dictionary mapping FieldType to Field objects
        """
        fields = {}
        patterns = self.get_patterns()
        
        # Extract card number (last 4 digits)
        if 'card_number' in patterns:
            for pattern in patterns['card_number']:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    full_number = match.group(1) if match.lastindex else match.group(0)
                    last_4 = full_number[-4:]
                    fields[FieldType.CARD_LAST_4_DIGITS] = Field(
                        field_type=FieldType.CARD_LAST_4_DIGITS,
                        value=last_4,
                        confidence=0.95,
                        snippet=match.group(0),
                        extraction_method="regex"
                    )
                    break
        
        # Extract card variant
        if 'card_variant' in patterns:
            for pattern in patterns['card_variant']:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    variant = match.group(1) if match.lastindex else match.group(0)
                    fields[FieldType.CARD_TYPE] = Field(
                        field_type=FieldType.CARD_TYPE,
                        value=variant.strip(),
                        confidence=0.9,
                        snippet=match.group(0),
                        extraction_method="regex"
                    )
                    break
        
        return fields

    def extract_billing_dates(self, text: str) -> Dict[FieldType, Field]:
        """
        Extract billing cycle and due date.
        
        Returns:
            Dictionary mapping FieldType to Field objects
        """
        fields = {}
        patterns = self.get_patterns()
        
        # Extract due date
        if 'due_date' in patterns:
            for pattern in patterns['due_date']:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    date_str = match.group(1) if match.lastindex else match.group(0)
                    parsed_date = parse_date(date_str)
                    if parsed_date:
                        fields[FieldType.PAYMENT_DUE_DATE] = Field(
                            field_type=FieldType.PAYMENT_DUE_DATE,
                            value=parsed_date.strftime("%Y-%m-%d"),
                            confidence=0.95,
                            snippet=match.group(0),
                            extraction_method="regex"
                        )
                        break
        
        # Extract billing cycle
        if 'billing_cycle' in patterns:
            for pattern in patterns['billing_cycle']:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    cycle_str = match.group(1) if match.lastindex else match.group(0)
                    fields[FieldType.STATEMENT_PERIOD_START] = Field(
                        field_type=FieldType.STATEMENT_PERIOD_START,
                        value=cycle_str.strip(),
                        confidence=0.9,
                        snippet=match.group(0),
                        extraction_method="regex"
                    )
                    break
        
        return fields

    def extract_balance(self, text: str) -> Dict[FieldType, Field]:
        """
        Extract balance and amount information.
        
        Returns:
            Dictionary mapping FieldType to Field objects
        """
        fields = {}
        patterns = self.get_patterns()
        
        # Extract total amount due
        if 'total_due' in patterns:
            for pattern in patterns['total_due']:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    amount_str = match.group(1) if match.lastindex else match.group(0)
                    amount = parse_currency(amount_str)
                    if amount is not None:
                        fields[FieldType.TOTAL_AMOUNT_DUE] = Field(
                            field_type=FieldType.TOTAL_AMOUNT_DUE,
                            value=amount,
                            confidence=0.95,
                            snippet=match.group(0),
                            extraction_method="regex"
                        )
                        break
        
        # Extract minimum amount due
        if 'minimum_due' in patterns:
            for pattern in patterns['minimum_due']:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    amount_str = match.group(1) if match.lastindex else match.group(0)
                    amount = parse_currency(amount_str)
                    if amount is not None:
                        fields[FieldType.MINIMUM_AMOUNT_DUE] = Field(
                            field_type=FieldType.MINIMUM_AMOUNT_DUE,
                            value=amount,
                            confidence=0.95,
                            snippet=match.group(0),
                            extraction_method="regex"
                        )
                        break
        
        return fields

    def extract_transactions(self, text: str) -> Field:
        """
        Extract transaction list from text.
        
        Returns:
            Field containing list of transactions
        """
        # This is a basic implementation
        # Subclasses should override for better table extraction
        transactions = []
        
        # Look for transaction patterns (date, description, amount)
        pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+(.*?)\s+([\d,]+\.?\d*)'
        matches = re.findall(pattern, text, re.MULTILINE)
        
        for match in matches[:50]:  # Limit to 50 transactions
            date_str, description, amount_str = match
            parsed_date = parse_date(date_str)
            amount = parse_currency(amount_str)
            
            if parsed_date and amount is not None:
                transactions.append({
                    "date": parsed_date.strftime("%Y-%m-%d"),
                    "description": description.strip()[:100],
                    "amount": amount
                })
        
        return transactions  # Return list, not Field
