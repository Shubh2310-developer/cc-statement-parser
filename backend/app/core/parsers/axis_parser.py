"""Axis Bank credit card statement parser."""
import re
from typing import Dict, List

from app.core.parsers.base import BaseParser
from app.models.enums import IssuerType, FieldType
from app.models.domain.field import Field


class AxisParser(BaseParser):
    """Parser for Axis Bank credit card statements."""

    def get_issuer_type(self) -> IssuerType:
        """Return Axis issuer type."""
        return IssuerType.AXIS

    def can_parse(self, text: str) -> tuple[bool, float]:
        """Check if this is an Axis statement."""
        markers = [
            r'Axis\s+Bank',
            r'axisbank\.com',
            r'MY\s+ZONE\s+CREDIT\s+CARD',
            r'MAGNUS\s+CREDIT\s+CARD',
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
        """Get Axis-specific regex patterns."""
        return {
            'card_number': [
                r'Card\s+No[:\s]+(\d{8}\*{4}\d{4})',
                r'(\d{8})\*{4}(\d{4})',  # Format: 45145700****5541
                r'Card\s+Number[:\s]+X+(\d{4})',
            ],
            'card_variant': [
                r'(MY\s+ZONE|MAGNUS|PRIVILEGE|SELECT|ACE)\s+(?:CREDIT\s+)?CARD',
                r'Axis\s+Bank\s+(.*?)\s+Credit\s+Card',
            ],
            'due_date': [
                r'Payment\s+Due\s+Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'Due\s+Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            ],
            'billing_cycle': [
                r'Statement\s+Period[:\s]+(.*?\d{2,4})',
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*-\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            ],
            'total_due': [
                r'Total\s+(?:Amount\s+)?Due[:\s]+(?:Rs\.?\s*)?([\d,]+\.?\d*)',
                r'Outstanding[:\s]+(?:Rs\.?\s*)?([\d,]+\.?\d*)\s+Dr',
            ],
            'minimum_due': [
                r'Minimum\s+(?:Amount\s+)?Due[:\s]+(?:Rs\.?\s*)?([\d,]+\.?\d*)',
                r'Minimum\s+Payment[:\s]+(?:Rs\.?\s*)?([\d,]+\.?\d*)',
            ],
        }

    def extract_card_info(self, text: str) -> Dict[FieldType, Field]:
        """Extract Axis-specific card information."""
        fields = super().extract_card_info(text)
        
        # Axis shows card number as 45145700****5541
        if FieldType.CARD_LAST_4_DIGITS not in fields:
            match = re.search(r'\d{8}\*{4}(\d{4})', text)
            if match:
                last_4 = match.group(1)
                fields[FieldType.CARD_LAST_4_DIGITS] = Field(
                    field_type=FieldType.CARD_LAST_4_DIGITS,
                    value=last_4,
                    confidence=0.95,
                    snippet=match.group(0),
                    extraction_method="regex"
                )
        
        return fields
