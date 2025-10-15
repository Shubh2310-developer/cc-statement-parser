"""ICICI Bank credit card statement parser with industry-grade extraction patterns."""
import re
from typing import Dict, List

from app.core.parsers.base import BaseParser
from app.models.enums import IssuerType, FieldType
from app.models.domain.field import Field


class ICICIParser(BaseParser):
    """
    Industry-grade parser for ICICI Bank credit card statements.

    Supports extraction of:
    - Card information (number, type, variant)
    - Statement periods and dates
    - Payment details and due dates
    - Balance information (credit limit, available credit)
    - Transaction history
    - Fees, interest, and rewards
    """

    def get_issuer_type(self) -> IssuerType:
        """Return ICICI issuer type."""
        return IssuerType.ICICI

    def can_parse(self, text: str) -> tuple[bool, float]:
        """
        Check if this is an ICICI statement using multiple validation markers.

        Args:
            text: PDF text content

        Returns:
            (can_parse, confidence_score)
        """
        # ICICI-specific markers with priority weights
        markers = [
            (r'ICICI\s+Bank\s+(?:Ltd|Limited)', 1.0),  # Primary marker
            (r'ICICI\s+Bank\s+Credit\s+Card', 0.9),
            (r'icicibank\.com', 0.7),
            (r'CIN\s+No\.?\s*L65190GJ1994PLC021012', 0.8),  # ICICI CIN
            (r'Platinum|Coral|Rubyx|Sapphiro.*ICICI', 0.6),
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
        Get comprehensive ICICI-specific regex patterns.

        Returns:
            Dictionary of field patterns with multiple pattern variants
        """
        return {
            # Card Information
            'card_number': [
                r'Card\s+(?:No|Number)[\s:]+(\d{4}[\s\*]+\d{4}[\s\*]+\d{4})',
                r'(\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4})',
                r'[X*]{4}\s+[X*]{4}\s+[X*]{4}\s+(\d{4})',
                r'Card\s+ending\s+(?:with|in)\s+(\d{4})',
                r'XXXX\s+XXXX\s+(\d{4})',
            ],
            'card_variant': [
                r'ICICI\s+Bank\s+(.*?)\s+Credit\s+Card',
                r'(Platinum|Gold|Coral|Rubyx|Sapphiro|Emeralde|Manchester\s+United)\s+Credit\s+Card',
                r'Credit\s+Card\s+(?:Type|Variant)[\s:]+(.+?)(?:\n|$)',
            ],
            'cardholder_name': [
                r'(?:Card\s+)?(?:Member|Holder)(?:\s+Name)?[\s:]+([A-Z][A-Z\s\.]+?)(?:\n|\s{2,})',
                r'Name[\s:]+([A-Z][A-Z\s\.]+?)(?:\n|$)',
                r'Dear\s+(?:Mr|Ms|Mrs)\.?\s+([A-Z][A-Z\s\.]+),',
                r'Primary\s+(?:Card\s+)?Member[\s:]+([A-Z][A-Z\s\.]+?)(?:\n|$)',
            ],

            # Statement Dates
            'statement_date': [
                r'STATEMENT\s+DATE[\s:]+(\d{1,2}[\s/\-]\w{3}[\s/\-]\d{2,4})',
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
                r'TOTAL\s+AMOUNT\s+DUE[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Total\s+Amount\s+due[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Current\s+(?:Total\s+)?Dues[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
                r'(?:Rs\.?|₹|`)\s*([\d,]+\.?\d{0,2})\s+(?:is\s+)?(?:the\s+)?Total',
            ],
            'minimum_due': [
                r'MINIMUM\s+(?:AMOUNT\s+)?DUE[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Minimum\s+(?:Amount\s+)?due[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Minimum\s+Payment[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Min(?:imum)?\s+Pay[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
            ],

            # Balance Information
            'credit_limit': [
                r'CREDIT\s+LIMIT[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Total\s+Credit\s+Limit[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Card\s+Limit[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
            ],
            'available_credit': [
                r'AVAILABLE\s+(?:CREDIT\s+)?LIMIT[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Available\s+Credit[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Credit\s+Available[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
            ],
            'opening_balance': [
                r'OPENING\s+BALANCE[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Previous\s+(?:Statement\s+)?Balance[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Balance\s+(?:b/f|brought\s+forward)[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
            ],
            'closing_balance': [
                r'CLOSING\s+BALANCE[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
                r'New\s+Balance[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Current\s+Balance[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Balance\s+(?:c/f|carried\s+forward)[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
            ],

            # Amounts and Charges
            'total_purchases': [
                r'Total\s+Purchases[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Purchase(?:s)?[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Retail\s+(?:Purchases|Transactions)[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
            ],
            'total_payments': [
                r'Total\s+Payment(?:s)?[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Payment(?:s)?\s+(?:Received|Made)[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Credits[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
            ],
            'total_fees': [
                r'Total\s+(?:Fees|Charges)[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Service\s+Charges[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Annual\s+Fee[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
            ],
            'total_interest': [
                r'(?:Finance|Interest)\s+Charges?[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Total\s+Interest[\s:]+(?:Rs\.?|₹|`)?[\s]*?([\d,]+\.?\d{0,2})',
            ],

            # Rewards and Points
            'reward_points': [
                r'(?:Reward|Payback)\s+Points?[\s:]+([0-9,]+)',
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

        # ICICI often shows partial card number - extract last 4 if not found
        if FieldType.CARD_LAST_4_DIGITS not in fields:
            extra_patterns = [
                r'[X*]{4}\s+[X*]{4}\s+[X*]{4}\s+(\d{4})',
                r'Card\s+ending\s+(?:with|in)\s+(\d{4})',
                r'XX+\s*(\d{4})',
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
        """Enhanced ICICI spatial extraction with detailed coordinate analysis."""
        from app.models.domain.extraction_result import ExtractionResult
        from app.utils.date_parser import parse_date
        from app.utils.logger import get_logger
        import uuid
        import fitz

        logger = get_logger(__name__)
        logger.info("Using detailed spatial extraction for ICICI Bank")

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

            logger.debug(f"Extracted {len(blocks)} text blocks from ICICI PDF")

            # 1. Card Last 4 Digits - Look for pattern "0000XXXXXXXX1265"
            for i, block in enumerate(blocks):
                if re.search(r'\d{4}[X*]+\d{4}', block["text"]):
                    # Extract last 4 digits
                    digits = re.findall(r'\d{4}', block["text"])
                    if digits:
                        last4 = digits[-1]
                        result.add_field(Field(
                            field_type=FieldType.CARD_LAST_4_DIGITS,
                            value=last4,
                            confidence=0.95,
                            snippet=block["text"],
                            extraction_method="spatial"
                        ))
                        logger.debug(f"Found card last 4: {last4}")
                        break

            # 2. Cardholder Name - Look for "MR/MS/MRS NAME" at top of document
            for i, block in enumerate(blocks[:30]):
                text_upper = block["text"].upper()
                # Check if starts with title and has name pattern
                if text_upper.startswith(("MR ", "MS ", "MRS ", "MR. ", "MS. ", "MRS. ")):
                    # Make sure it's a name and not some other text
                    name_text = block["text"].strip()
                    # Remove title prefix
                    for prefix in ["MR ", "MS ", "MRS ", "MR. ", "MS. ", "MRS. "]:
                        if name_text.upper().startswith(prefix):
                            name_text = name_text[len(prefix):].strip()
                            break

                    # Check if it looks like a name (letters and spaces only)
                    if name_text and re.match(r'^[A-Z][A-Z\s]+$', name_text):
                        result.add_field(Field(
                            field_type=FieldType.CARDHOLDER_NAME,
                            value=name_text.title(),
                            confidence=0.90,
                            snippet=block["text"],
                            extraction_method="spatial"
                        ))
                        logger.debug(f"Found cardholder name: {name_text}")
                        break

            # 3. Statement Date - Find "STATEMENT DATE" label and value below
            for i, block in enumerate(blocks):
                if "STATEMENT DATE" in block["text"].upper():
                    label_y = block["y"]
                    label_x = block["center_x"]
                    # Look for date in next few blocks
                    for j in range(i+1, min(i+15, len(blocks))):
                        candidate = blocks[j]
                        y_diff = candidate["y"] - label_y
                        x_diff = abs(candidate["center_x"] - label_x)

                        # Check if it's below the label and aligned
                        if 5 < y_diff < 40 and x_diff < 50:
                            # Try to parse as date
                            parsed = parse_date(candidate["text"])
                            if parsed:
                                result.add_field(Field(
                                    field_type=FieldType.STATEMENT_DATE,
                                    value=parsed.strftime("%Y-%m-%d"),
                                    confidence=0.95,
                                    snippet=candidate["text"],
                                    extraction_method="spatial"
                                ))
                                logger.debug(f"Found statement date: {parsed.strftime('%Y-%m-%d')}")
                                break
                    break

            # 4. Payment Due Date - Find "PAYMENT DUE DATE" label
            for i, block in enumerate(blocks):
                if "PAYMENT DUE DATE" in block["text"].upper():
                    label_y = block["y"]
                    label_x = block["center_x"]
                    for j in range(i+1, min(i+15, len(blocks))):
                        candidate = blocks[j]
                        y_diff = candidate["y"] - label_y
                        x_diff = abs(candidate["center_x"] - label_x)

                        if 5 < y_diff < 40 and x_diff < 50:
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

            # 5. Total Amount Due - Look for exact label match
            for i, block in enumerate(blocks):
                if block["text"].strip() == "Total Amount due":
                    label_y = block["y"]
                    label_x = block["center_x"]
                    for j in range(i+1, min(i+20, len(blocks))):
                        candidate = blocks[j]
                        y_diff = candidate["y"] - label_y
                        x_diff = abs(candidate["center_x"] - label_x)

                        if 5 < y_diff < 40 and x_diff < 40:
                            # Extract amount
                            amount_text = candidate["text"].replace(',', '').replace('`', '').replace('₹', '').replace('Rs', '').strip()
                            if re.match(r'^\d+(\.\d{1,2})?$', amount_text):
                                result.add_field(Field(
                                    field_type=FieldType.TOTAL_AMOUNT_DUE,
                                    value=float(amount_text),
                                    confidence=0.95,
                                    snippet=candidate["text"],
                                    extraction_method="spatial"
                                ))
                                logger.debug(f"Found total amount due: {amount_text}")
                                break
                    break

            # 6. Minimum Amount Due
            for i, block in enumerate(blocks):
                if block["text"].strip() == "Minimum Amount due":
                    label_y = block["y"]
                    label_x = block["center_x"]
                    for j in range(i+1, min(i+20, len(blocks))):
                        candidate = blocks[j]
                        y_diff = candidate["y"] - label_y
                        x_diff = abs(candidate["center_x"] - label_x)

                        if 5 < y_diff < 40 and x_diff < 40:
                            amount_text = candidate["text"].replace(',', '').replace('`', '').replace('₹', '').replace('Rs', '').strip()
                            if re.match(r'^\d+(\.\d{1,2})?$', amount_text):
                                result.add_field(Field(
                                    field_type=FieldType.MINIMUM_AMOUNT_DUE,
                                    value=float(amount_text),
                                    confidence=0.95,
                                    snippet=candidate["text"],
                                    extraction_method="spatial"
                                ))
                                logger.debug(f"Found minimum amount due: {amount_text}")
                                break
                    break

            # 7. Credit Limit - Column-based extraction
            credit_headers = {}
            for i, block in enumerate(blocks):
                text_clean = block["text"].strip()
                if text_clean == "Credit Limit":
                    credit_headers['credit_limit'] = (i, block["center_x"], block["y"])
                elif text_clean == "Available Credit":
                    credit_headers['available_credit'] = (i, block["center_x"], block["y"])

            for key, (idx, header_x, header_y) in credit_headers.items():
                for j in range(idx+1, min(idx+25, len(blocks))):
                    candidate = blocks[j]
                    y_diff = candidate["y"] - header_y
                    x_diff = abs(candidate["center_x"] - header_x)

                    # Column alignment check
                    if 10 < y_diff < 50 and x_diff < 35:
                        amount_text = candidate["text"].replace(',', '').replace('`', '').replace('₹', '').replace('Rs', '').strip()
                        if re.match(r'^\d+(\.\d{1,2})?$', amount_text):
                            field_type = FieldType.CREDIT_LIMIT if key == 'credit_limit' else FieldType.AVAILABLE_CREDIT
                            result.add_field(Field(
                                field_type=field_type,
                                value=float(amount_text),
                                confidence=0.95,
                                snippet=candidate["text"],
                                extraction_method="spatial"
                            ))
                            logger.debug(f"Found {key}: {amount_text}")
                            break

            # 8. Previous Balance (Opening Balance)
            for i, block in enumerate(blocks):
                if block["text"].strip() == "Previous Balance":
                    label_y = block["y"]
                    label_x = block["center_x"]
                    for j in range(i+1, min(i+20, len(blocks))):
                        candidate = blocks[j]
                        y_diff = candidate["y"] - label_y
                        x_diff = abs(candidate["center_x"] - label_x)

                        if 5 < y_diff < 40 and x_diff < 50:
                            amount_text = candidate["text"].replace(',', '').replace('`', '').replace('₹', '').replace('Rs', '').strip()
                            if re.match(r'^\d+(\.\d{1,2})?$', amount_text):
                                result.add_field(Field(
                                    field_type=FieldType.OPENING_BALANCE,
                                    value=float(amount_text),
                                    confidence=0.90,
                                    snippet=candidate["text"],
                                    extraction_method="spatial"
                                ))
                                logger.debug(f"Found previous balance: {amount_text}")
                                break
                    break

            doc.close()
            logger.info(f"ICICI spatial extraction completed: {result.field_count} fields")

        except Exception as e:
            logger.error(f"ICICI spatial parsing failed: {e}", exc_info=True)
            # Fallback to regex-based parsing
            full_text = page.get_text() if 'page' in locals() else text
            if 'doc' in locals():
                doc.close()
            return self.parse(full_text, extracted_fields)

        return result
