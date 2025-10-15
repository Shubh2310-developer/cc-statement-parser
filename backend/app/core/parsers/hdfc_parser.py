"""HDFC Bank credit card statement parser with industry-grade extraction patterns."""
import re
from typing import Dict, List
from decimal import Decimal

from app.core.parsers.base import BaseParser
from app.models.enums import IssuerType, FieldType
from app.models.domain.field import Field


class HDFCParser(BaseParser):
    """
    Industry-grade parser for HDFC Bank credit card statements.

    Supports extraction of:
    - Card information (number, type, variant)
    - Statement periods and dates
    - Payment details and due dates
    - Balance information (credit limit, available credit)
    - Transaction history
    - Fees, interest, and rewards
    """

    def get_issuer_type(self) -> IssuerType:
        """Return HDFC issuer type."""
        return IssuerType.HDFC

    def can_parse(self, text: str) -> tuple[bool, float]:
        """
        Check if this is an HDFC statement using multiple validation markers.

        Args:
            text: PDF text content

        Returns:
            (can_parse, confidence_score)
        """
        # HDFC-specific markers with priority weights
        markers = [
            (r'HDFC\s+Bank\s+(?:Ltd|Limited)', 1.0),  # Primary marker
            (r'HDFC\s+BANK\s+CREDIT\s+CARD', 0.9),
            (r'hdfcbank\.com', 0.7),
            (r'IndianOil\s+HDFC', 0.8),
            (r'Regalia|Millennia|Diners\s+Club.*HDFC', 0.6),
        ]

        total_confidence = 0.0
        matches = 0

        for pattern, weight in markers:
            if re.search(pattern, text, re.IGNORECASE):
                total_confidence += weight
                matches += 1

        if matches >= 1:
            # Normalize confidence between 0.7 and 0.98
            confidence = min(0.98, 0.7 + (total_confidence * 0.1))
            return (True, confidence)

        return (False, 0.0)

    def get_patterns(self) -> Dict[str, List[str]]:
        """
        Get comprehensive HDFC-specific regex patterns.

        Returns:
            Dictionary of field patterns with multiple pattern variants
        """
        return {
            # Card Information
            'card_number': [
                r'(?:Card\s+(?:No|Number|#)[\s:]*)?(\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4})',
                r'(\d{16})',  # 16-digit continuous
                r'Card\s+ending\s+with\s+(\d{4})',
                r'XX+\s*(\d{4})',  # Masked format
            ],
            'card_variant': [
                r'((?:Regalia|Millennia|Diners\s+Club|Platinum|MoneyBack|Freedom|Titanium)(?:\s+\w+)*)\s+Credit\s+Card',
                r'HDFC\s+Bank\s+(.*?)\s+Credit\s+Card',
                r'(IndianOil\s+HDFC\s+Bank)\s+Credit\s+Card',
                r'Credit\s+Card\s+(?:Type|Variant)[\s:]+(.+?)(?:\n|$)',
            ],
            'cardholder_name': [
                r'(?:Card\s+)?(?:Member|Holder)[\s:]+([A-Z][A-Z\s\.]+?)(?:\n|\s{2,})',
                r'Name\s*:\s*([A-Z][A-Z\s\.]+?)(?:\n|$)',
                r'Dear\s+([A-Z][A-Z\s\.]+),',
            ],

            # Statement Dates
            'statement_date': [
                r'Statement\s+Date[\s:]+(\d{1,2}[\s/\-]\w{3}[\s/\-]\d{2,4})',
                r'Statement\s+(?:as\s+on|on)[\s:]+(\d{1,2}[\s/\-]\d{1,2}[\s/\-]\d{2,4})',
                r'(?:Date|Generated)[\s:]+(\d{1,2}[\s/\-]\d{1,2}[\s/\-]\d{2,4})',
            ],
            'billing_cycle': [
                r'(?:Statement|Billing)\s+Period[\s:]+(\d{1,2}[\s/\-]\w{3}[\s/\-]\d{2,4})\s+to\s+(\d{1,2}[\s/\-]\w{3}[\s/\-]\d{2,4})',
                r'(\d{1,2}[\s/\-]\d{1,2}[\s/\-]\d{2,4})\s+to\s+(\d{1,2}[\s/\-]\d{1,2}[\s/\-]\d{2,4})',
                r'From\s+(\d{1,2}[\s/\-]\w{3}[\s/\-]\d{2,4})\s+To\s+(\d{1,2}[\s/\-]\w{3}[\s/\-]\d{2,4})',
            ],

            # Payment Information
            'due_date': [
                r'Payment\s+Due\s+(?:Date|By)[\s:]+(\d{1,2}[\s/\-]\w{3}[\s/\-]\d{2,4})',
                r'Due\s+Date[\s:]+(\d{1,2}[\s/\-]\d{1,2}[\s/\-]\d{2,4})',
                r'Pay\s+By[\s:]+(\d{1,2}[\s/\-]\d{1,2}[\s/\-]\d{2,4})',
                r'(?:Last|Final)\s+Date[\s:]+(\d{1,2}[\s/\-]\d{1,2}[\s/\-]\d{2,4})',
            ],
            'total_due': [
                r'Total\s+Amount\s+Due[\s:]+(?:Rs\.?|₹|INR)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Current\s+(?:Total\s+)?Outstanding[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Amount\s+Payable[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'(?:Rs\.?|₹)\s*([\d,]+\.?\d{0,2})\s+(?:is\s+)?(?:the\s+)?Total(?:\s+Amount)?\s+Due',
            ],
            'minimum_due': [
                r'Minimum\s+(?:Amount\s+)?Due[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Min(?:imum)?\s+Payment(?:\s+Due)?[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Minimum\s+Pay[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
            ],

            # Balance Information
            'credit_limit': [
                r'Credit\s+Limit[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Total\s+Credit\s+Limit[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Sanctioned\s+Limit[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
            ],
            'available_credit': [
                r'Available\s+Credit(?:\s+Limit)?[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Credit\s+Available[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
            ],
            'opening_balance': [
                r'Opening\s+Balance[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Previous\s+(?:Statement\s+)?Balance[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
            ],
            'closing_balance': [
                r'Closing\s+Balance[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'New\s+Balance[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Current\s+Balance[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
            ],

            # Amounts and Charges
            'total_purchases': [
                r'Total\s+Purchases[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Purchase(?:s)?(?:\s+Amount)?[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
            ],
            'total_payments': [
                r'Total\s+Payments(?:\s+Received)?[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Payments?(?:\s+Made)?[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
            ],
            'total_fees': [
                r'Total\s+(?:Fees|Charges)[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Service\s+Charges[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
            ],
            'total_interest': [
                r'(?:Finance|Interest)\s+Charges?[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
                r'Total\s+Interest[\s:]+(?:Rs\.?|₹)?[\s]*?([\d,]+\.?\d{0,2})',
            ],

            # Rewards and Points
            'reward_points': [
                r'(?:Reward|Loyalty)\s+Points?(?:\s+Balance)?[\s:]+([0-9,]+)',
                r'(?:Points|Miles)(?:\s+Earned)?[\s:]+([0-9,]+)',
                r'Total\s+Points[\s:]+([0-9,]+)',
            ],

            # Customer Information
            'customer_id': [
                r'Customer\s+(?:ID|Number|Code)[\s:]+([A-Z0-9]+)',
                r'Client\s+ID[\s:]+([A-Z0-9]+)',
            ],
            'statement_number': [
                r'Statement\s+(?:No|Number|#)[\s:]+([A-Z0-9\-]+)',
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

        # Extract cardholder name
        if 'cardholder_name' in patterns:
            for pattern in patterns['cardholder_name']:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    name = match.group(1).strip()
                    # Clean up name
                    name = re.sub(r'\s+', ' ', name)
                    if len(name) > 3 and not re.search(r'\d', name):  # Validate
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
                        # Pattern with two date groups
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
