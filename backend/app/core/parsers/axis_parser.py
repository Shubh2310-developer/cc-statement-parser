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


    def parse_with_pdf(self, pdf_bytes: bytes, text: str, extracted_fields=None):
        """Enhanced Axis spatial extraction with detailed coordinate analysis."""
        from app.models.domain.extraction_result import ExtractionResult
        from app.models.domain.field import Field
        from app.models.enums import FieldType
        from app.utils.date_parser import parse_date
        from app.utils.logger import get_logger
        import uuid
        import fitz
        import re

        logger = get_logger(__name__)
        logger.info("Using detailed spatial extraction for Axis Bank")

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

            # Extract all text with positions
            text_dict = page.get_text("dict")
            blocks = []
            for block in text_dict.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text_content = span["text"].strip()
                            if text_content:
                                blocks.append({
                                    "text": text_content,
                                    "x": span["bbox"][0],
                                    "y": span["bbox"][1],
                                    "x2": span["bbox"][2],
                                    "y2": span["bbox"][3],
                                    "center_x": (span["bbox"][0] + span["bbox"][2]) / 2,
                                    "center_y": (span["bbox"][1] + span["bbox"][3]) / 2,
                                })

            blocks.sort(key=lambda b: (b["y"], b["x"]))

            logger.debug(f"Extracted {len(blocks)} text blocks from Axis PDF")

            # Get full text for regex patterns
            full_text = page.get_text()

            # 1. Card Last 4 Digits - "Card No: 45145700****5541"
            card_match = re.search(r'Card\s+No[:\s]+\d{4,8}\*+(\d{4})', full_text, re.IGNORECASE)
            if card_match:
                result.add_field(Field(
                    field_type=FieldType.CARD_LAST_4_DIGITS,
                    value=card_match.group(1),
                    confidence=0.95,
                    snippet=card_match.group(0),
                    extraction_method="spatial"
                ))
                logger.debug(f"Found card last 4: {card_match.group(1)}")

            # 2. Cardholder Name - Look at top of page or after "Name" label
            # Try top of page first (in address section)
            for i, block in enumerate(blocks[:15]):
                if re.match(r'^[A-Z][a-z]+\s+[a-z]+$', block["text"]):
                    result.add_field(Field(
                        field_type=FieldType.CARDHOLDER_NAME,
                        value=block["text"].title(),
                        confidence=0.90,
                        snippet=block["text"],
                        extraction_method="spatial"
                    ))
                    logger.debug(f"Found cardholder name: {block['text']}")
                    break

            # If not found, try after "Name" label
            if FieldType.CARDHOLDER_NAME not in result.fields:
                for i, block in enumerate(blocks):
                    if block["text"].strip() == "Name" and i + 1 < len(blocks):
                        next_block = blocks[i + 1]
                        if abs(next_block["y"] - block["y"]) < 5:
                            name_text = next_block["text"].strip()
                            if re.match(r'^[A-Za-z][A-Za-z\s]+$', name_text) and len(name_text) > 3:
                                result.add_field(Field(
                                    field_type=FieldType.CARDHOLDER_NAME,
                                    value=name_text.title(),
                                    confidence=0.90,
                                    snippet=name_text,
                                    extraction_method="spatial"
                                ))
                                logger.debug(f"Found cardholder name: {name_text}")
                                break

            # 3. Customer ID
            cust_match = re.search(r'CUSTOMER\s+ID\s+(\d+)', full_text, re.IGNORECASE)
            if cust_match:
                result.add_field(Field(
                    field_type=FieldType.CUSTOMER_ID,
                    value=cust_match.group(1),
                    confidence=0.95,
                    snippet=cust_match.group(0),
                    extraction_method="spatial"
                ))
                logger.debug(f"Found customer ID: {cust_match.group(1)}")

            # 4. Statement Period - "19/10/2019 - 18/11/2019"
            period_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})\s*-\s*(\d{1,2}/\d{1,2}/\d{4})', full_text)
            if period_match:
                start_date = parse_date(period_match.group(1))
                end_date = parse_date(period_match.group(2))
                if start_date:
                    result.add_field(Field(
                        field_type=FieldType.STATEMENT_PERIOD_START,
                        value=start_date.strftime("%Y-%m-%d"),
                        confidence=0.95,
                        snippet=period_match.group(1),
                        extraction_method="spatial"
                    ))
                    logger.debug(f"Found statement start: {start_date.strftime('%Y-%m-%d')}")
                if end_date:
                    result.add_field(Field(
                        field_type=FieldType.STATEMENT_PERIOD_END,
                        value=end_date.strftime("%Y-%m-%d"),
                        confidence=0.95,
                        snippet=period_match.group(2),
                        extraction_method="spatial"
                    ))
                    logger.debug(f"Found statement end: {end_date.strftime('%Y-%m-%d')}")

            # 5. Payment Due Date - Table header with value below
            for i, block in enumerate(blocks):
                if block["text"].strip() == "Payment Due Date":
                    label_x = block["center_x"]
                    label_y = block["y"]
                    for j in range(i+1, min(i+20, len(blocks))):
                        candidate = blocks[j]
                        y_diff = candidate["y"] - label_y
                        x_diff = abs(candidate["center_x"] - label_x)

                        if 5 < y_diff < 50 and x_diff < 50:
                            # Try to parse as date
                            parsed = parse_date(candidate["text"])
                            if parsed:
                                result.add_field(Field(
                                    field_type=FieldType.PAYMENT_DUE_DATE,
                                    value=parsed.strftime("%Y-%m-%d"),
                                    confidence=0.95,
                                    snippet=candidate["text"],
                                    extraction_method="spatial"
                                ))
                                logger.debug(f"Found payment due date: {parsed.strftime('%Y-%m-%d')}")
                                break
                    break

            # 6. Statement Generation Date
            stmt_date_match = re.search(r'Statement\s+Generation\s+Date\s+(\d{1,2}/\d{1,2}/\d{4})', full_text, re.IGNORECASE)
            if stmt_date_match:
                parsed = parse_date(stmt_date_match.group(1))
                if parsed:
                    result.add_field(Field(
                        field_type=FieldType.STATEMENT_DATE,
                        value=parsed.strftime("%Y-%m-%d"),
                        confidence=0.95,
                        snippet=stmt_date_match.group(1),
                        extraction_method="spatial"
                    ))
                    logger.debug(f"Found statement date: {parsed.strftime('%Y-%m-%d')}")

            # 7. Total Payment Due - Table header with value below
            for i, block in enumerate(blocks):
                if block["text"].strip() == "Total Payment Due":
                    label_x = block["center_x"]
                    label_y = block["y"]
                    # Find value below this label
                    for j in range(i+1, min(i+20, len(blocks))):
                        candidate = blocks[j]
                        y_diff = candidate["y"] - label_y
                        x_diff = abs(candidate["center_x"] - label_x)

                        if 5 < y_diff < 50 and x_diff < 50:
                            # Check if it's an amount with "Dr"
                            amount_match = re.match(r'([\d,]+\.?\d{0,2})\s+Dr', candidate["text"])
                            if amount_match:
                                amount_text = amount_match.group(1).replace(',', '')
                                result.add_field(Field(
                                    field_type=FieldType.TOTAL_AMOUNT_DUE,
                                    value=float(amount_text),
                                    confidence=0.95,
                                    snippet=candidate["text"],
                                    extraction_method="spatial"
                                ))
                                logger.debug(f"Found total payment due: {amount_text}")
                                break
                    break

            # 8. Minimum Payment Due - Table header with value below
            for i, block in enumerate(blocks):
                if block["text"].strip() == "Minimum Payment Due":
                    label_x = block["center_x"]
                    label_y = block["y"]
                    # Find value below this label
                    for j in range(i+1, min(i+20, len(blocks))):
                        candidate = blocks[j]
                        y_diff = candidate["y"] - label_y
                        x_diff = abs(candidate["center_x"] - label_x)

                        if 5 < y_diff < 50 and x_diff < 50:
                            amount_match = re.match(r'([\d,]+\.?\d{0,2})\s+Dr', candidate["text"])
                            if amount_match:
                                amount_text = amount_match.group(1).replace(',', '')
                                result.add_field(Field(
                                    field_type=FieldType.MINIMUM_AMOUNT_DUE,
                                    value=float(amount_text),
                                    confidence=0.95,
                                    snippet=candidate["text"],
                                    extraction_method="spatial"
                                ))
                                logger.debug(f"Found minimum payment due: {amount_text}")
                                break
                    break

            # 9. Credit Limit - Table header with value below
            for i, block in enumerate(blocks):
                if block["text"].strip() == "Credit Limit":
                    label_x = block["center_x"]
                    label_y = block["y"]
                    for j in range(i+1, min(i+20, len(blocks))):
                        candidate = blocks[j]
                        y_diff = candidate["y"] - label_y
                        x_diff = abs(candidate["center_x"] - label_x)

                        if 5 < y_diff < 50 and x_diff < 50:
                            amount_match = re.match(r'^([\d,]+\.?\d{0,2})$', candidate["text"].strip())
                            if amount_match:
                                amount_text = amount_match.group(1).replace(',', '')
                                result.add_field(Field(
                                    field_type=FieldType.CREDIT_LIMIT,
                                    value=float(amount_text),
                                    confidence=0.95,
                                    snippet=candidate["text"],
                                    extraction_method="spatial"
                                ))
                                logger.debug(f"Found credit limit: {amount_text}")
                                break
                    break

            # 10. Available Credit Limit - Table header with value below
            for i, block in enumerate(blocks):
                if block["text"].strip() == "Available Credit Limit":
                    label_x = block["center_x"]
                    label_y = block["y"]
                    for j in range(i+1, min(i+20, len(blocks))):
                        candidate = blocks[j]
                        y_diff = candidate["y"] - label_y
                        x_diff = abs(candidate["center_x"] - label_x)

                        if 5 < y_diff < 50 and x_diff < 50:
                            amount_match = re.match(r'^([\d,]+\.?\d{0,2})$', candidate["text"].strip())
                            if amount_match:
                                amount_text = amount_match.group(1).replace(',', '')
                                result.add_field(Field(
                                    field_type=FieldType.AVAILABLE_CREDIT,
                                    value=float(amount_text),
                                    confidence=0.95,
                                    snippet=candidate["text"],
                                    extraction_method="spatial"
                                ))
                                logger.debug(f"Found available credit: {amount_text}")
                                break
                    break

            # 11. Previous Balance
            prev_balance_match = re.search(r'Previous\s+Balance[^\d]+([\d,]+\.?\d{0,2})\s+Dr', full_text, re.IGNORECASE)
            if prev_balance_match:
                amount_text = prev_balance_match.group(1).replace(',', '')
                result.add_field(Field(
                    field_type=FieldType.OPENING_BALANCE,
                    value=float(amount_text),
                    confidence=0.90,
                    snippet=prev_balance_match.group(0),
                    extraction_method="spatial"
                ))
                logger.debug(f"Found previous balance: {amount_text}")

            doc.close()
            logger.info(f"Axis spatial extraction completed: {result.field_count} fields")

        except Exception as e:
            logger.error(f"Axis spatial parsing failed: {e}", exc_info=True)
            # Fallback to regex-based parsing
            full_text = page.get_text() if 'page' in locals() else text
            if 'doc' in locals():
                doc.close()
            return self.parse(full_text, extracted_fields)

        return result
