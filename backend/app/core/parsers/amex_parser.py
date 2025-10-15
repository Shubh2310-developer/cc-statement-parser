"""American Express credit card statement parser."""
import re
from typing import Dict, List

from app.core.parsers.base import BaseParser
from app.models.enums import IssuerType, FieldType
from app.models.domain.field import Field


class AmexParser(BaseParser):
    """Parser for American Express credit card statements."""

    def get_issuer_type(self) -> IssuerType:
        """Return Amex issuer type."""
        return IssuerType.AMEX

    def can_parse(self, text: str) -> tuple[bool, float]:
        """Check if this is an Amex statement."""
        markers = [
            r'American\s+Express',
            r'AMEX',
            r'americanexpress\.com',
            r'Membership\s+Number',
        ]
        
        matches = 0
        for marker in markers:
            if re.search(marker, text, re.IGNORECASE):
                matches += 1
        
        if matches >= 1:
            confidence = min(0.95, 0.7 + (matches * 0.15))
            return (True, confidence)
        
        return (False, 0.0)

    def get_patterns(self) -> Dict[str, List[str]]:
        """Get Amex-specific regex patterns."""
        return {
            'card_number': [
                r'Membership\s+Number[:\s]+X+-X+-(\d{5})',
                r'XXXX-XXXXXX-(\d{5})',  # Amex format
                r'Card\s+ending[:\s]+(\d{5})',
            ],
            'card_variant': [
                r'(Platinum\s+Travel|Gold|Membership\s+Rewards)\s+Credit\s+Card',
                r'American\s+Express[®]?\s+(.*?)\s+Credit\s+Card',
            ],
            'due_date': [
                r'Payment\s+Due\s+Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'Due\s+Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'Please\s+pay\s+by[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            ],
            'billing_cycle': [
                r'Statement\s+Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            ],
            'total_due': [
                r'Closing\s+Balance[:\s]+Rs\.?\s*([\d,]+\.?\d*)',
                r'Total\s+Amount\s+Due[:\s]+Rs\.?\s*([\d,]+\.?\d*)',
                r'New\s+Balance[:\s]+Rs\.?\s*([\d,]+\.?\d*)',
            ],
            'minimum_due': [
                r'Minimum\s+Payment[:\s]+Rs\.?\s*([\d,]+\.?\d*)',
                r'Minimum\s+Amount\s+Due[:\s]+Rs\.?\s*([\d,]+\.?\d*)',
            ],
        }

    def extract_card_info(self, text: str) -> Dict[FieldType, Field]:
        """Extract Amex-specific card information."""
        fields = super().extract_card_info(text)
        
        # Amex shows card number as XXXX-XXXXXX-31005
        if FieldType.CARD_LAST_4_DIGITS not in fields:
            match = re.search(r'XXXX-XXXXXX-(\d{5})', text)
            if match:
                last_5 = match.group(1)
                # For Amex, use last 5 digits but store as "last 4" field
                fields[FieldType.CARD_LAST_4_DIGITS] = Field(
                    field_type=FieldType.CARD_LAST_4_DIGITS,
                    value=last_5,
                    confidence=0.95,
                    snippet=match.group(0),
                    extraction_method="regex",
                    metadata={"note": "Amex uses 5 digits"}
                )
        
        return fields
