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


    def parse_with_pdf(self, pdf_bytes: bytes, text: str, extracted_fields=None):
        """Enhanced Amex spatial extraction with detailed analysis."""
        from app.models.domain.extraction_result import ExtractionResult
        from app.models.domain.field import Field
        from app.models.enums import FieldType
        from app.utils.date_parser import parse_date
        from app.utils.logger import get_logger
        import uuid
        import fitz
        import re

        logger = get_logger(__name__)
        logger.info("Using detailed spatial extraction for American Express")

        result = ExtractionResult(
            id=str(uuid.uuid4()),
            job_id="",
            document_id="",
            issuer=self.get_issuer_type(),
            raw_text=text[:500] if text else ""
        )

        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            page = doc[0]

            # Get full text for regex patterns
            full_text = page.get_text()

            logger.debug(f"Extracted text from Amex PDF")

            # 1. Cardholder Name - Line after "Prepared for"
            lines = full_text.split('\n')
            for i, line in enumerate(lines):
                if 'Prepared for' in line and i + 1 < len(lines):
                    # Skip headers, get the name line
                    for j in range(i + 1, min(i + 5, len(lines))):
                        candidate = lines[j].strip()
                        if candidate and re.match(r'^[A-Z][A-Z\s]+$', candidate) and len(candidate) > 5:
                            result.add_field(Field(
                                field_type=FieldType.CARDHOLDER_NAME,
                                value=candidate.title(),
                                confidence=0.90,
                                snippet=candidate,
                                extraction_method="spatial"
                            ))
                            logger.debug(f"Found cardholder name: {candidate}")
                            break
                    break

            # 2. Card Last 5 Digits (Amex uses 15-digit cards)
            card_match = re.search(r'XXXX-XXXXXX-(\d{5})', full_text)
            if card_match:
                result.add_field(Field(
                    field_type=FieldType.CARD_LAST_4_DIGITS,
                    value=card_match.group(1),
                    confidence=0.95,
                    snippet=f"XXXX-XXXXXX-{card_match.group(1)}",
                    extraction_method="spatial"
                ))
                logger.debug(f"Found card last 5: {card_match.group(1)}")

            # 3. Statement Date
            date_match = re.search(r'Date\s+(\d{1,2}/\d{1,2}/\d{4})', full_text)
            if date_match:
                parsed = parse_date(date_match.group(1))
                if parsed:
                    result.add_field(Field(
                        field_type=FieldType.STATEMENT_DATE,
                        value=parsed.strftime("%Y-%m-%d"),
                        confidence=0.95,
                        snippet=date_match.group(1),
                        extraction_method="spatial"
                    ))
                    logger.debug(f"Found statement date: {parsed.strftime('%Y-%m-%d')}")
                    statement_year = parsed.year
                else:
                    statement_year = 2022

            # 4-6. Parse the balance table (lines 6-16)
            # Find the table header row and extract values from corresponding rows
            header_idx = -1
            for i, line in enumerate(lines):
                if 'Opening Balance Rs' in line:
                    header_idx = i
                    break

            if header_idx >= 0 and header_idx + 11 < len(lines):
                # Collect amount lines starting 5 lines after header row
                # header_idx is "Opening Balance Rs" line
                # Values start at header_idx + 5
                amount_lines = []
                for j in range(header_idx + 5, header_idx + 12):
                    if j < len(lines):
                        amount_lines.append(lines[j])

                # Opening Balance Rs value is at amount_lines[0]
                if len(amount_lines) > 0:
                    opening_match = re.search(r'([\d,]+\.?\d{0,2})', amount_lines[0])
                    if opening_match:
                        amount_text = opening_match.group(1).replace(',', '')
                        result.add_field(Field(
                            field_type=FieldType.OPENING_BALANCE,
                            value=float(amount_text),
                            confidence=0.95,
                            snippet=opening_match.group(1),
                            extraction_method="spatial"
                        ))
                        logger.debug(f"Found opening balance: {amount_text}")

                # Closing Balance Rs value is at amount_lines[4]
                if len(amount_lines) > 4:
                    closing_match = re.search(r'([\d,]+\.?\d{0,2})', amount_lines[4])
                    if closing_match:
                        amount_text = closing_match.group(1).replace(',', '')
                        result.add_field(Field(
                            field_type=FieldType.TOTAL_AMOUNT_DUE,
                            value=float(amount_text),
                            confidence=0.95,
                            snippet=closing_match.group(1),
                            extraction_method="spatial"
                        ))
                        logger.debug(f"Found closing balance: {amount_text}")

                # Minimum Payment Rs value is at amount_lines[5]
                if len(amount_lines) > 5:
                    min_match = re.search(r'([\d,]+\.?\d{0,2})', amount_lines[5])
                    if min_match:
                        amount_text = min_match.group(1).replace(',', '')
                        result.add_field(Field(
                            field_type=FieldType.MINIMUM_AMOUNT_DUE,
                            value=float(amount_text),
                            confidence=0.95,
                            snippet=min_match.group(1),
                            extraction_method="spatial"
                        ))
                        logger.debug(f"Found minimum payment: {amount_text}")

            # 7. Statement Period - "From April 21 to May 20, 2022"
            period_match = re.search(r'From\s+(\w+\s+\d{1,2})\s+to\s+(\w+\s+\d{1,2}),\s+(\d{4})', full_text)
            if period_match:
                year = period_match.group(3)
                start_parsed = parse_date(f"{period_match.group(1)}, {year}")
                end_parsed = parse_date(f"{period_match.group(2)}, {year}")
                if start_parsed:
                    result.add_field(Field(
                        field_type=FieldType.STATEMENT_PERIOD_START,
                        value=start_parsed.strftime("%Y-%m-%d"),
                        confidence=0.95,
                        snippet=period_match.group(1),
                        extraction_method="spatial"
                    ))
                    logger.debug(f"Found statement start: {start_parsed.strftime('%Y-%m-%d')}")
                if end_parsed:
                    result.add_field(Field(
                        field_type=FieldType.STATEMENT_PERIOD_END,
                        value=end_parsed.strftime("%Y-%m-%d"),
                        confidence=0.95,
                        snippet=period_match.group(2),
                        extraction_method="spatial"
                    ))
                    logger.debug(f"Found statement end: {end_parsed.strftime('%Y-%m-%d')}")

            # 8. Credit Limit Rs - Look for "Credit Summary" section
            for i, line in enumerate(lines):
                if 'Credit Summary' in line:
                    # Headers are on next lines (Credit Limit Rs, Available Credit Limit Rs)
                    # Skip the date line ("At May 20, 2022")
                    # Then get the two amount values
                    amounts_found = []
                    for j in range(i + 1, min(i + 8, len(lines))):
                        # Skip lines that contain dates or text
                        if re.match(r'^At\s+', lines[j]) or re.search(r'Limit\s+Rs', lines[j]):
                            continue
                        # Look for pure amount lines (large amounts with commas)
                        amount_match = re.match(r'^([\d,]+\.?\d{0,2})$', lines[j].strip())
                        if amount_match:
                            amt_text = amount_match.group(1)
                            # Make sure it's a large amount (> 1000)
                            amt_val = float(amt_text.replace(',', ''))
                            if amt_val > 1000:
                                amounts_found.append(amt_text)

                    # First amount is Credit Limit, second is Available Credit
                    if len(amounts_found) >= 2:
                        credit_limit_text = amounts_found[0].replace(',', '')
                        result.add_field(Field(
                            field_type=FieldType.CREDIT_LIMIT,
                            value=float(credit_limit_text),
                            confidence=0.95,
                            snippet=amounts_found[0],
                            extraction_method="spatial"
                        ))
                        logger.debug(f"Found credit limit: {credit_limit_text}")

                        avail_credit_text = amounts_found[1].replace(',', '')
                        result.add_field(Field(
                            field_type=FieldType.AVAILABLE_CREDIT,
                            value=float(avail_credit_text),
                            confidence=0.95,
                            snippet=amounts_found[1],
                            extraction_method="spatial"
                        ))
                        logger.debug(f"Found available credit: {avail_credit_text}")
                    break

            doc.close()
            logger.info(f"Amex spatial extraction completed: {result.field_count} fields")

        except Exception as e:
            logger.error(f"Amex spatial parsing failed: {e}", exc_info=True)
            # Fallback to regex-based parsing
            full_text = page.get_text() if 'page' in locals() else text
            if 'doc' in locals():
                doc.close()
            return self.parse(full_text, extracted_fields)

        return result
