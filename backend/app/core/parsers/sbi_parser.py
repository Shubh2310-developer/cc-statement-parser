"""SBI Card statement parser with industry-grade extraction patterns."""
import re
from typing import Dict, List

from app.core.parsers.base import BaseParser
from app.models.enums import IssuerType, FieldType
from app.models.domain.field import Field


class SBIParser(BaseParser):
    """
    Industry-grade parser for SBI Card statements.

    Supports extraction of:
    - Card information (number, type, variant)
    - Statement periods and dates
    - Payment details and due dates
    - Balance information (credit limit, available credit)
    - Transaction history
    - Fees, interest, and rewards
    """

    def get_issuer_type(self) -> IssuerType:
        """Return SBI issuer type."""
        return IssuerType.SBI

    def can_parse(self, text: str) -> tuple[bool, float]:
        """
        Check if this is an SBI Card statement using multiple validation markers.

        Args:
            text: PDF text content

        Returns:
            (can_parse, confidence_score)
        """
        # SBI Card-specific markers with priority weights
        markers = [
            (r'SBI\s+Card(?:s)?(?:\s+Ltd)?', 1.0),  # Primary marker
            (r'State\s+Bank\s+of\s+India.*Card', 0.9),
            (r'sbicard\.com', 0.7),
            (r'SimplySAVE|SimplyClick|BPCL|IRCTC.*SBI', 0.6),
            (r'CIN\s*:\s*U65999MH1998PLC116939', 0.8),  # SBI Card CIN
        ]

        total_confidence = 0.0
        matches = 0

        for pattern, weight in markers:
            if re.search(pattern, text, re.IGNORECASE):
                total_confidence += weight
                matches += 1

        if matches >= 1:
            confidence = min(0.98, 0.7 + (total_confidence * 0.1))
            return (True, confidence)

        return (False, 0.0)

    def get_patterns(self) -> Dict[str, List[str]]:
        """
        Get comprehensive SBI Card-specific regex patterns.

        Returns:
            Dictionary of field patterns with multiple pattern variants
        """
        return {
            # Card Information
            'card_number': [
                r'Card\s+(?:No|Number)[\s:]+(\d{4}[\s\*\-]+\d{4}[\s\*\-]+\d{4}[\s\*\-]+\d{4})',
                r'(\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4})',
                r'[X*]{4}[\s\-]+[X*]{4}[\s\-]+[X*]{4}[\s\-]+(\d{4})',
                r'Card\s+ending\s+(?:with|in)\s+(\d{4})',
                r'XX+\s*XX+\s*XX+\s*(\d{4})',
            ],
            'card_variant': [
                r'(SimplySAVE|SimplyClick|Elite|Platinum|BPCL|IRCTC|Unnati|Prime)\s+(?:SBI\s+)?Card',
                r'SBI\s+Card\s+(SimplySAVE|SimplyClick|Elite|Platinum|BPCL|IRCTC|Unnati|Prime)',
                r'Credit\s+Card\s+(?:Type|Variant)[\s:]+(.+?)(?:\n|$)',
            ],
            'cardholder_name': [
                r'(?:Mr|Ms|Mrs)\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',  # Title with dot and proper name
                r'Dear\s+(?:Mr|Ms|Mrs)\.?\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
                r'(?:Card\s+)?(?:Member|Holder)(?:\s+Name)?[\s:]+([A-Z][A-Z\s\.]+?)(?:\n|\s{2,})',
                r'(?:Primary\s+)?Cardholder[\s:]+([A-Z][A-Z\s\.]+?)(?:\n|$)',
            ],

            # Statement Dates
            'statement_date': [
                r'Statement\s+Date[\s:]+(\d{1,2}[\s/\-]\w{3}[\s/\-]\d{2,4})',
                r'Statement\s+(?:as\s+on|Date)[\s:]+(\d{1,2}[\s/\-]\d{1,2}[\s/\-]\d{2,4})',
                r'(?:Generated|Issued)\s+(?:on|Date)[\s:]+(\d{1,2}[\s/\-]\d{1,2}[\s/\-]\d{2,4})',
            ],
            'billing_cycle': [
                r'(?:Statement|Billing)\s+Period[\s:]+(\d{1,2}[\s/\-]\w{3}[\s/\-]\d{2,4})\s+to\s+(\d{1,2}[\s/\-]\w{3}[\s/\-]\d{2,4})',
                r'From\s+(\d{1,2}[\s/\-]\d{1,2}[\s/\-]\d{2,4})\s+To\s+(\d{1,2}[\s/\-]\d{1,2}[\s/\-]\d{2,4})',
                r'(\d{1,2}[\s/\-]\d{1,2}[\s/\-]\d{2,4})\s*-\s*(\d{1,2}[\s/\-]\d{1,2}[\s/\-]\d{2,4})',
            ],

            # Payment Information
            'due_date': [
                r'PAYMENT\s+DUE\s+DATE[\s:]+(\d{1,2}[\s/\-]\w{3}[\s/\-]\d{2,4})',
                r'Payment\s+Due\s+(?:Date|By)[\s:]+(\d{1,2}[\s/\-]\d{1,2}[\s/\-]\d{2,4})',
                r'Due\s+Date[\s:]+(\d{1,2}[\s/\-]\d{1,2}[\s/\-]\d{2,4})',
                r'Pay\s+(?:by|before)[\s:]+(\d{1,2}[\s/\-]\d{1,2}[\s/\-]\d{2,4})',
            ],
            'total_due': [
                r'TOTAL\s+AMOUNT\s+DUE[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Total\s+Amount\s+[Dd]ue[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Current\s+(?:Total\s+)?(?:Outstanding|Dues)[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'(?:Rs\.?|₹)\s*([\d,]+\.?\d{0,2})\s+(?:is\s+)?(?:the\s+)?Total',
            ],
            'minimum_due': [
                r'MINIMUM\s+(?:AMOUNT\s+)?DUE[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Minimum\s+(?:Amount\s+)?[Dd]ue[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Minimum\s+Payment[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Min(?:imum)?\s+Pay[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
            ],

            # Balance Information
            'credit_limit': [
                r'CREDIT\s+LIMIT[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Total\s+Credit\s+Limit[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Card\s+Limit[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
            ],
            'available_credit': [
                r'AVAILABLE\s+(?:CREDIT\s+)?LIMIT[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Available\s+Credit[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Credit\s+Available[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
            ],
            'opening_balance': [
                r'OPENING\s+BALANCE[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Previous\s+(?:Statement\s+)?Balance[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Balance\s+(?:b/f|brought\s+forward)[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
            ],
            'closing_balance': [
                r'CLOSING\s+BALANCE[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'New\s+Balance[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Current\s+Balance[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Balance\s+(?:c/f|carried\s+forward)[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
            ],

            # Amounts and Charges
            'total_purchases': [
                r'Total\s+Purchases[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Purchase(?:s)?[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Retail\s+(?:Purchases|Transactions)[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
            ],
            'total_payments': [
                r'Total\s+Payment(?:s)?[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Payment(?:s)?\s+(?:Received|Made)[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Credits[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
            ],
            'total_fees': [
                r'Total\s+(?:Fees|Charges)[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Service\s+Charges[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Annual\s+Fee[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
            ],
            'total_interest': [
                r'(?:Finance|Interest)\s+Charges?[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Total\s+Interest[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
            ],

            # Rewards and Points
            'reward_points': [
                r'(?:Reward|Loyalty)\s+Points?[\s:]+([0-9,]+)',
                r'Points\s+Balance[\s:]+([0-9,]+)',
                r'Accumulated\s+Points[\s:]+([0-9,]+)',
                r'Total\s+Points[\s:]+([0-9,]+)',
            ],

            # Customer Information
            'customer_id': [
                r'Customer\s+(?:ID|Number)[\s:]+([A-Z0-9]+)',
                r'CIF\s+(?:No|Number)[\s:]+([A-Z0-9]+)',
                r'Member\s+ID[\s:]+([A-Z0-9]+)',
            ],
            'statement_number': [
                r'Statement\s+(?:No|Number)[\s:]+([A-Z0-9\-]+)',
                r'Reference\s+(?:No|Number)[\s:]+([A-Z0-9\-]+)',
            ],
        }

    def extract_card_info(self, text: str) -> Dict[FieldType, Field]:
        """
        Extract comprehensive card-related information.

        Returns:
            Dictionary mapping FieldType to Field objects
        """
        fields = super().extract_card_info(text)
        patterns = self.get_patterns()

        # SBI Card often shows partial card number - extract last 4 if not found
        if FieldType.CARD_LAST_4_DIGITS not in fields:
            extra_patterns = [
                r'[X*]{4}[\s\-]+[X*]{4}[\s\-]+[X*]{4}[\s\-]+(\d{4})',
                r'Card\s+ending\s+(?:with|in)\s+(\d{4})',
                r'XX+\s*XX+\s*XX+\s*(\d{4})',
            ]

            for pattern in extra_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    last_4 = match.group(1)
                    fields[FieldType.CARD_LAST_4_DIGITS] = Field(
                        field_type=FieldType.CARD_LAST_4_DIGITS,
                        value=last_4,
                        confidence=0.95,
                        snippet=match.group(0),
                        extraction_method="regex"
                    )
                    break

        # Extract cardholder name
        if 'cardholder_name' in patterns:
            for pattern in patterns['cardholder_name']:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    name = match.group(1).strip()
                    name = re.sub(r'\s+', ' ', name)
                    if len(name) > 3 and not re.search(r'\d', name):
                        fields[FieldType.CARDHOLDER_NAME] = Field(
                            field_type=FieldType.CARDHOLDER_NAME,
                            value=name.title(),
                            confidence=0.9,
                            snippet=match.group(0)[:100],
                            extraction_method="regex"
                        )
                        break

        # Extract customer ID
        if 'customer_id' in patterns:
            for pattern in patterns['customer_id']:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    customer_id = match.group(1).strip()
                    fields[FieldType.CUSTOMER_ID] = Field(
                        field_type=FieldType.CUSTOMER_ID,
                        value=customer_id,
                        confidence=0.95,
                        snippet=match.group(0),
                        extraction_method="regex"
                    )
                    break

        # Extract statement number
        if 'statement_number' in patterns:
            for pattern in patterns['statement_number']:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    stmt_num = match.group(1).strip()
                    fields[FieldType.STATEMENT_NUMBER] = Field(
                        field_type=FieldType.STATEMENT_NUMBER,
                        value=stmt_num,
                        confidence=0.95,
                        snippet=match.group(0),
                        extraction_method="regex"
                    )
                    break

        return fields

    def extract_billing_dates(self, text: str) -> Dict[FieldType, Field]:
        """
        Extract comprehensive billing cycle and date information.

        Returns:
            Dictionary mapping FieldType to Field objects
        """
        fields = super().extract_billing_dates(text)
        patterns = self.get_patterns()

        # Extract statement date
        if 'statement_date' in patterns and FieldType.STATEMENT_DATE not in fields:
            from app.utils.date_parser import parse_date
            for pattern in patterns['statement_date']:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    date_str = match.group(1)
                    parsed_date = parse_date(date_str)
                    if parsed_date:
                        fields[FieldType.STATEMENT_DATE] = Field(
                            field_type=FieldType.STATEMENT_DATE,
                            value=parsed_date.strftime("%Y-%m-%d"),
                            confidence=0.95,
                            snippet=match.group(0),
                            extraction_method="regex"
                        )
                        break

        # Extract billing cycle (start and end dates)
        if 'billing_cycle' in patterns:
            from app.utils.date_parser import parse_date
            for pattern in patterns['billing_cycle']:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    if match.lastindex >= 2:
                        start_str = match.group(1)
                        end_str = match.group(2)

                        start_date = parse_date(start_str)
                        end_date = parse_date(end_str)

                        if start_date:
                            fields[FieldType.STATEMENT_PERIOD_START] = Field(
                                field_type=FieldType.STATEMENT_PERIOD_START,
                                value=start_date.strftime("%Y-%m-%d"),
                                confidence=0.95,
                                snippet=match.group(0),
                                extraction_method="regex"
                            )

                        if end_date:
                            fields[FieldType.STATEMENT_PERIOD_END] = Field(
                                field_type=FieldType.STATEMENT_PERIOD_END,
                                value=end_date.strftime("%Y-%m-%d"),
                                confidence=0.95,
                                snippet=match.group(0),
                                extraction_method="regex"
                            )
                        break

        return fields

    def extract_balance(self, text: str) -> Dict[FieldType, Field]:
        """
        Extract comprehensive balance and amount information.

        Returns:
            Dictionary mapping FieldType to Field objects
        """
        fields = super().extract_balance(text)
        patterns = self.get_patterns()
        from app.utils.currency_parser import parse_currency

        # Additional amount fields
        amount_fields = [
            ('credit_limit', FieldType.CREDIT_LIMIT),
            ('available_credit', FieldType.AVAILABLE_CREDIT),
            ('opening_balance', FieldType.OPENING_BALANCE),
            ('closing_balance', FieldType.CLOSING_BALANCE),
            ('total_purchases', FieldType.TOTAL_PURCHASES),
            ('total_payments', FieldType.TOTAL_PAYMENTS),
            ('total_fees', FieldType.TOTAL_FEES),
            ('total_interest', FieldType.TOTAL_INTEREST),
        ]

        for pattern_key, field_type in amount_fields:
            if pattern_key in patterns and field_type not in fields:
                for pattern in patterns[pattern_key]:
                    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                    if match:
                        amount_str = match.group(1) if match.lastindex else match.group(0)
                        amount = parse_currency(amount_str)
                        if amount is not None:
                            fields[field_type] = Field(
                                field_type=field_type,
                                value=amount,
                                confidence=0.92,
                                snippet=match.group(0)[:100],
                                extraction_method="regex"
                            )
                            break

        # Extract reward points
        if 'reward_points' in patterns:
            for pattern in patterns['reward_points']:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    points_str = match.group(1).replace(',', '')
                    try:
                        points = int(points_str)
                        fields[FieldType.REWARD_POINTS] = Field(
                            field_type=FieldType.REWARD_POINTS,
                            value=points,
                            confidence=0.9,
                            snippet=match.group(0),
                            extraction_method="regex"
                        )
                        break
                    except ValueError:
                        continue

        return fields

    def parse_with_pdf(self, pdf_bytes: bytes, text: str, extracted_fields=None):
        """
        Enhanced parsing using spatial layout information for SBI statements.

        Args:
            pdf_bytes: Raw PDF bytes
            text: Extracted text
            extracted_fields: Pre-extracted fields (optional)

        Returns:
            ExtractionResult with spatially-extracted fields
        """
        from app.models.domain.extraction_result import ExtractionResult
        from app.utils.date_parser import parse_date
        from app.utils.logger import get_logger
        import uuid
        import fitz

        logger = get_logger(__name__)
        logger.info("Using spatial-aware extraction for SBI Card")

        # Create result object
        result = ExtractionResult(
            id=str(uuid.uuid4()),
            job_id="",
            document_id="",
            issuer=self.get_issuer_type(),
            raw_text=text[:500]
        )

        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            page = doc[0]

            # Extract text with positions
            text_dict = page.get_text("dict")
            blocks = []
            for block in text_dict.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            blocks.append({
                                "text": span["text"].strip(),
                                "y": span["bbox"][1],
                                "x": span["bbox"][0],
                            })

            blocks.sort(key=lambda b: (b["y"], b["x"]))

            # Extract card last 4
            for block in blocks:
                if re.search(r'X+\s+X+\s+X+\s+\w{4}', block["text"]):
                    parts = block["text"].split()
                    if len(parts) >= 4:
                        result.add_field(Field(
                            field_type=FieldType.CARD_LAST_4_DIGITS,
                            value=parts[-1],
                            confidence=0.95,
                            snippet=block["text"],
                            extraction_method="spatial"
                        ))
                    break

            # Extract label-value pairs
            for i, block in enumerate(blocks):
                text_lower = block["text"].lower()

                # Statement Date
                if text_lower == "statement date":
                    for j in range(i+1, min(i+10, len(blocks))):
                        candidate = blocks[j]["text"]
                        if re.search(r'\d{1,2}\s+\w+\s+\d{4}', candidate) and "to" not in candidate.lower():
                            parsed = parse_date(candidate)
                            if parsed:
                                result.add_field(Field(
                                    field_type=FieldType.STATEMENT_DATE,
                                    value=parsed.strftime("%Y-%m-%d"),
                                    confidence=0.95,
                                    snippet=candidate,
                                    extraction_method="spatial"
                                ))
                            break

                # Credit Limit
                if "credit limit" in text_lower and "available" not in text_lower:
                    for j in range(i+1, min(i+8, len(blocks))):
                        if re.search(r'^[\d,]+\.?\d{0,2}$', blocks[j]["text"]):
                            result.add_field(Field(
                                field_type=FieldType.CREDIT_LIMIT,
                                value=float(blocks[j]["text"].replace(',', '')),
                                confidence=0.95,
                                snippet=blocks[j]["text"],
                                extraction_method="spatial"
                            ))
                            break

                # Available Credit
                if "available credit limit" in text_lower:
                    for j in range(i+1, min(i+8, len(blocks))):
                        if re.search(r'^[\d,]+\.?\d{0,2}$', blocks[j]["text"]):
                            result.add_field(Field(
                                field_type=FieldType.AVAILABLE_CREDIT,
                                value=float(blocks[j]["text"].replace(',', '')),
                                confidence=0.95,
                                snippet=blocks[j]["text"],
                                extraction_method="spatial"
                            ))
                            break

                # Total Amount Due
                if ("total amount due" in text_lower or "*total amount due" in text_lower):
                    for j in range(i+1, min(i+10, len(blocks))):
                        if re.search(r'^[\d,]+\.?\d{0,2}$', blocks[j]["text"]):
                            result.add_field(Field(
                                field_type=FieldType.TOTAL_AMOUNT_DUE,
                                value=float(blocks[j]["text"].replace(',', '')),
                                confidence=0.95,
                                snippet=blocks[j]["text"],
                                extraction_method="spatial"
                            ))
                            break

                # Minimum Amount Due
                if ("minimum amount due" in text_lower or "**minimum amount due" in text_lower):
                    for j in range(i+1, min(i+10, len(blocks))):
                        if re.search(r'^[\d,]+\.?\d{0,2}$', blocks[j]["text"]):
                            result.add_field(Field(
                                field_type=FieldType.MINIMUM_AMOUNT_DUE,
                                value=float(blocks[j]["text"].replace(',', '')),
                                confidence=0.95,
                                snippet=blocks[j]["text"],
                                extraction_method="spatial"
                            ))
                            break

                # Payment Due Date
                if "payment due date" in text_lower:
                    for j in range(i+1, min(i+6, len(blocks))):
                        candidate = blocks[j]["text"]
                        if "NO PAYMENT" in candidate.upper():
                            result.add_field(Field(
                                field_type=FieldType.PAYMENT_DUE_DATE,
                                value="No payment required",
                                confidence=0.95,
                                snippet=candidate,
                                extraction_method="spatial"
                            ))
                            break
                        elif re.search(r'\d{1,2}\s+\w+\s+\d{4}', candidate):
                            parsed = parse_date(candidate)
                            if parsed:
                                result.add_field(Field(
                                    field_type=FieldType.PAYMENT_DUE_DATE,
                                    value=parsed.strftime("%Y-%m-%d"),
                                    confidence=0.95,
                                    snippet=candidate,
                                    extraction_method="spatial"
                                ))
                            break

            # Cardholder name from top
            for block in blocks[:15]:
                if block["y"] < 80 and re.match(r'^[A-Z][A-Z\s]{5,40}$', block["text"]):
                    words = block["text"].split()
                    if 2 <= len(words) <= 4 and not any(kw in block["text"].upper() for kw in ["GSTIN", "CARD", "NUMBER"]):
                        result.add_field(Field(
                            field_type=FieldType.CARDHOLDER_NAME,
                            value=block["text"].title(),
                            confidence=0.90,
                            snippet=block["text"],
                            extraction_method="spatial"
                        ))
                        break

            # Statement period
            period_match = re.search(r'Statement\s+Period[\s:]*(\d{1,2}\s+\w+\s+\d{2,4})\s+to\s+(\d{1,2}\s+\w+\s+\d{2,4})', text, re.IGNORECASE)
            if period_match:
                start_parsed = parse_date(period_match.group(1))
                end_parsed = parse_date(period_match.group(2))
                if start_parsed:
                    result.add_field(Field(
                        field_type=FieldType.STATEMENT_PERIOD_START,
                        value=start_parsed.strftime("%Y-%m-%d"),
                        confidence=0.95,
                        snippet=period_match.group(0),
                        extraction_method="spatial"
                    ))
                if end_parsed:
                    result.add_field(Field(
                        field_type=FieldType.STATEMENT_PERIOD_END,
                        value=end_parsed.strftime("%Y-%m-%d"),
                        confidence=0.95,
                        snippet=period_match.group(0),
                        extraction_method="spatial"
                    ))

            # Card variant
            full_text = page.get_text()
            variant_match = re.search(r'(SimplySAVE|SimplyClick|Elite|Platinum|BPCL|IRCTC)\s*(?:SBI)?', full_text, re.IGNORECASE)
            if variant_match:
                result.add_field(Field(
                    field_type=FieldType.CARD_VARIANT,
                    value=variant_match.group(1),
                    confidence=0.90,
                    snippet=variant_match.group(0),
                    extraction_method="spatial"
                ))

            doc.close()
            logger.info(f"Spatial extraction completed: {result.field_count} fields")

        except Exception as e:
            logger.error(f"Spatial parsing failed: {e}", exc_info=True)
            # Fall back to regex parsing
            return self.parse(text, extracted_fields)

        return result
