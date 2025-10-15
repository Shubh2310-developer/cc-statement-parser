"""Spatial-aware SBI Card parser using coordinate-based extraction."""
import re
import fitz
from typing import Dict, List, Optional, Any, Tuple
from app.core.parsers.sbi_parser import SBIParser
from app.models.domain.field import Field
from app.models.enums import FieldType
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SBISpatialParser(SBIParser):
    """Enhanced SBI parser with spatial coordinate awareness."""

    def parse_with_pdf(self, pdf_bytes: bytes, text: str) -> Dict[str, Field]:
        """
        Parse SBI statement using spatial layout information.

        Args:
            pdf_bytes: Raw PDF bytes
            text: Extracted text (for fallback)

        Returns:
            Dictionary of extracted fields
        """
        logger.info("Using spatial-aware parsing for SBI Card statement")

        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            page = doc[0]  # Focus on first page for metadata

            # Extract text with bounding boxes
            text_dict = page.get_text("dict")
            blocks = self._extract_text_blocks(text_dict)

            # Build spatial index
            spatial_index = self._build_spatial_index(blocks)

            # Extract fields using spatial relationships
            fields = {}

            # Card number (last 4 digits)
            card_last4 = self._extract_card_number(blocks, spatial_index)
            if card_last4:
                fields['card_last_4'] = Field(
                    field_type=FieldType.CARD_LAST_4_DIGITS,
                    value=card_last4,
                    confidence=0.95,
                    source_text=card_last4
                )

            # Statement date
            stmt_date = self._extract_statement_date(blocks, spatial_index)
            if stmt_date:
                fields['statement_date'] = Field(
                    field_type=FieldType.STATEMENT_DATE,
                    value=stmt_date,
                    confidence=0.95,
                    source_text=stmt_date
                )

            # Credit limit
            credit_limit = self._extract_credit_limit(blocks, spatial_index)
            if credit_limit:
                fields['credit_limit'] = Field(
                    field_type=FieldType.CREDIT_LIMIT,
                    value=float(credit_limit.replace(',', '')),
                    confidence=0.95,
                    source_text=credit_limit
                )

            # Total amount due
            total_due = self._extract_total_due(blocks, spatial_index)
            if total_due:
                fields['total_amount_due'] = Field(
                    field_type=FieldType.TOTAL_AMOUNT_DUE,
                    value=float(total_due.replace(',', '')),
                    confidence=0.95,
                    source_text=total_due
                )

            # Minimum amount due
            min_due = self._extract_minimum_due(blocks, spatial_index)
            if min_due:
                fields['minimum_amount_due'] = Field(
                    field_type=FieldType.MINIMUM_AMOUNT_DUE,
                    value=float(min_due.replace(',', '')),
                    confidence=0.95,
                    source_text=min_due
                )

            # Available credit
            avail_credit = self._extract_available_credit(blocks, spatial_index)
            if avail_credit:
                fields['available_credit'] = Field(
                    field_type=FieldType.AVAILABLE_CREDIT,
                    value=float(avail_credit.replace(',', '')),
                    confidence=0.95,
                    source_text=avail_credit
                )

            # Payment due date
            due_date = self._extract_due_date(blocks, spatial_index)
            if due_date:
                fields['payment_due_date'] = Field(
                    field_type=FieldType.PAYMENT_DUE_DATE,
                    value=due_date,
                    confidence=0.95,
                    source_text=due_date
                )

            # Cardholder name (from top of statement)
            cardholder = self._extract_cardholder_name(blocks, spatial_index)
            if cardholder:
                fields['cardholder_name'] = Field(
                    field_type=FieldType.CARDHOLDER_NAME,
                    value=cardholder,
                    confidence=0.90,
                    source_text=cardholder
                )

            # Statement period
            period_start, period_end = self._extract_statement_period(text)
            if period_start:
                fields['statement_period_start'] = Field(
                    field_type=FieldType.STATEMENT_PERIOD_START,
                    value=period_start,
                    confidence=0.95,
                    source_text=f"Statement Period: {period_start} to {period_end}"
                )
            if period_end:
                fields['statement_period_end'] = Field(
                    field_type=FieldType.STATEMENT_PERIOD_END,
                    value=period_end,
                    confidence=0.95,
                    source_text=f"Statement Period: {period_start} to {period_end}"
                )

            doc.close()
            logger.info(f"Spatial extraction completed: {len(fields)} fields")
            return fields

        except Exception as e:
            logger.error(f"Spatial parsing failed: {e}", exc_info=True)
            # Fallback to regex-based parsing
            return {}

    def _extract_text_blocks(self, text_dict: Dict) -> List[Dict]:
        """Extract text blocks with positions."""
        blocks = []
        for block in text_dict.get("blocks", []):
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        blocks.append({
                            "text": span["text"].strip(),
                            "bbox": span["bbox"],
                            "x": span["bbox"][0],
                            "y": span["bbox"][1],
                            "x2": span["bbox"][2],
                            "y2": span["bbox"][3]
                        })
        return blocks

    def _build_spatial_index(self, blocks: List[Dict]) -> Dict[str, List[Dict]]:
        """Build index of text blocks by Y coordinate."""
        index = {}
        for block in blocks:
            y_key = int(block["y"] / 5) * 5  # Group by 5px buckets
            if y_key not in index:
                index[y_key] = []
            index[y_key].append(block)
        return index

    def _find_value_near_label(self, blocks: List[Dict], label: str, y_tolerance: int = 20, x_direction: str = "right") -> Optional[str]:
        """Find value near a label based on spatial proximity."""
        label_lower = label.lower()

        for i, block in enumerate(blocks):
            if label_lower in block["text"].lower():
                label_y = block["y"]
                label_x = block["x"]

                # Look for value in nearby blocks
                candidates = []
                for other in blocks:
                    y_diff = abs(other["y"] - label_y)
                    if y_diff <= y_tolerance:
                        if x_direction == "right" and other["x"] > label_x:
                            candidates.append((other, y_diff, other["x"] - label_x))
                        elif x_direction == "below":
                            if other["y"] > label_y:
                                candidates.append((other, abs(other["x"] - label_x), other["y"] - label_y))

                # Sort by distance and return closest
                if candidates:
                    candidates.sort(key=lambda c: (c[1], c[2]))
                    return candidates[0][0]["text"]

        return None

    def _extract_card_number(self, blocks: List[Dict], spatial_index: Dict) -> Optional[str]:
        """Extract card last 4 digits."""
        # Look for pattern XXXX XXXX XXXX XX56
        pattern = r'X+\s+X+\s+X+\s+X+(\d{2})'
        for block in blocks:
            match = re.search(pattern, block["text"])
            if match:
                # SBI shows last 2 digits - need to find full last 4
                last2 = match.group(1)
                # Look for XX56 pattern
                full_pattern = r'XX(\d{2})'
                full_match = re.search(full_pattern, block["text"])
                if full_match:
                    return "XX" + full_match.group(1)

        # Fallback: search for any XXXX pattern
        for block in blocks:
            if re.search(r'X{4}\s+X{4}\s+X{4}\s+\w{4}', block["text"]):
                parts = block["text"].split()
                if len(parts) >= 4:
                    last_part = parts[-1]
                    if len(last_part) == 4:
                        return last_part

        return None

    def _extract_statement_date(self, blocks: List[Dict], spatial_index: Dict) -> Optional[str]:
        """Extract statement date using spatial relationship."""
        value = self._find_value_near_label(blocks, "Statement Date", y_tolerance=30, x_direction="below")
        if value and re.search(r'\d{1,2}\s+\w+\s+\d{4}', value):
            return self._normalize_date(value)
        return None

    def _extract_credit_limit(self, blocks: List[Dict], spatial_index: Dict) -> Optional[str]:
        """Extract credit limit."""
        value = self._find_value_near_label(blocks, "Credit Limit", y_tolerance=30, x_direction="below")
        if value and re.search(r'[\d,]+\.?\d{0,2}', value):
            return re.search(r'([\d,]+\.?\d{0,2})', value).group(1)
        return None

    def _extract_total_due(self, blocks: List[Dict], spatial_index: Dict) -> Optional[str]:
        """Extract total amount due."""
        value = self._find_value_near_label(blocks, "*Total Amount Due", y_tolerance=40, x_direction="below")
        if value and re.search(r'[\d,]+\.?\d{0,2}', value):
            return re.search(r'([\d,]+\.?\d{0,2})', value).group(1)
        return None

    def _extract_minimum_due(self, blocks: List[Dict], spatial_index: Dict) -> Optional[str]:
        """Extract minimum amount due."""
        value = self._find_value_near_label(blocks, "**Minimum Amount Due", y_tolerance=40, x_direction="below")
        if value and re.search(r'[\d,]+\.?\d{0,2}', value):
            return re.search(r'([\d,]+\.?\d{0,2})', value).group(1)
        return None

    def _extract_available_credit(self, blocks: List[Dict], spatial_index: Dict) -> Optional[str]:
        """Extract available credit limit."""
        value = self._find_value_near_label(blocks, "Available Credit Limit", y_tolerance=30, x_direction="below")
        if value and re.search(r'[\d,]+\.?\d{0,2}', value):
            return re.search(r'([\d,]+\.?\d{0,2})', value).group(1)
        return None

    def _extract_due_date(self, blocks: List[Dict], spatial_index: Dict) -> Optional[str]:
        """Extract payment due date."""
        value = self._find_value_near_label(blocks, "Payment Due Date", y_tolerance=30, x_direction="below")
        if value:
            # Handle "NO PAYMENT REQUIRED" case
            if "NO PAYMENT" in value.upper():
                return "No payment required"
            if re.search(r'\d{1,2}\s+\w+\s+\d{4}', value):
                return self._normalize_date(value)
        return None

    def _extract_cardholder_name(self, blocks: List[Dict], spatial_index: Dict) -> Optional[str]:
        """Extract cardholder name from top of statement."""
        # Name appears near top, look for all-caps names
        for block in blocks[:20]:  # Check first 20 blocks
            if block["y"] < 100:  # Top portion
                text = block["text"]
                # Check if it's a name (all caps, 2-3 words)
                if re.match(r'^[A-Z][A-Z\s]{5,40}$', text):
                    words = text.split()
                    if 2 <= len(words) <= 4:
                        return text.title()
        return None

    def _extract_statement_period(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract statement period from text."""
        pattern = r'(?:for\s+)?Statement\s+Period[\s:]*(\d{1,2}\s+\w+\s+\d{2,4})\s+to\s+(\d{1,2}\s+\w+\s+\d{2,4})'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return self._normalize_date(match.group(1)), self._normalize_date(match.group(2))
        return None, None

    def _normalize_date(self, date_str: str) -> str:
        """Normalize date to YYYY-MM-DD format."""
        from app.utils.date_parser import parse_date
        try:
            parsed = parse_date(date_str)
            if parsed:
                return parsed.strftime("%Y-%m-%d")
        except:
            pass
        return date_str
