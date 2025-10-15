"""Spatial-aware extraction utilities for layout-based PDFs."""
import re
import fitz
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TextBlock:
    """Represents a text block with spatial coordinates."""
    text: str
    x: float
    y: float
    x2: float
    y2: float
    width: float
    height: float

    @property
    def center_x(self) -> float:
        """Get center X coordinate."""
        return (self.x + self.x2) / 2

    @property
    def center_y(self) -> float:
        """Get center Y coordinate."""
        return (self.y + self.y2) / 2


class SpatialExtractor:
    """
    Spatial-aware text extraction for layout-based PDFs.

    Handles PDFs where labels and values are positioned spatially
    rather than being inline with colons or other delimiters.
    """

    def __init__(self):
        """Initialize spatial extractor."""
        self.logger = logger

    def extract_blocks(self, pdf_bytes: bytes, page_num: int = 0) -> List[TextBlock]:
        """
        Extract text blocks with spatial coordinates from a PDF page.

        Args:
            pdf_bytes: Raw PDF bytes
            page_num: Page number to extract (0-indexed)

        Returns:
            List of TextBlock objects sorted by position
        """
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")

            if page_num >= len(doc):
                logger.warning(f"Page {page_num} exceeds document length {len(doc)}")
                page_num = 0

            page = doc[page_num]
            text_dict = page.get_text("dict")

            blocks = []
            for block in text_dict.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            bbox = span["bbox"]
                            text = span["text"].strip()
                            if text:  # Skip empty strings
                                blocks.append(TextBlock(
                                    text=text,
                                    x=bbox[0],
                                    y=bbox[1],
                                    x2=bbox[2],
                                    y2=bbox[3],
                                    width=bbox[2] - bbox[0],
                                    height=bbox[3] - bbox[1]
                                ))

            # Sort by Y position (top to bottom), then X (left to right)
            blocks.sort(key=lambda b: (b.y, b.x))

            doc.close()
            logger.debug(f"Extracted {len(blocks)} text blocks from page {page_num}")
            return blocks

        except Exception as e:
            logger.error(f"Failed to extract blocks: {e}", exc_info=True)
            return []

    def find_value_below_label(
        self,
        blocks: List[TextBlock],
        label: str,
        y_tolerance: float = 50.0,
        x_tolerance: float = 30.0,
        value_pattern: Optional[str] = None
    ) -> Optional[str]:
        """
        Find a value positioned below a label.

        Args:
            blocks: List of text blocks
            label: Label text to search for (case-insensitive)
            y_tolerance: Maximum Y distance between label and value
            x_tolerance: Maximum X distance (for alignment check)
            value_pattern: Optional regex pattern the value must match

        Returns:
            Extracted value or None
        """
        label_lower = label.lower()

        for i, block in enumerate(blocks):
            if label_lower in block.text.lower():
                label_y = block.y
                label_x = block.x

                # Look for values in subsequent blocks
                for j in range(i + 1, min(i + 15, len(blocks))):
                    candidate = blocks[j]

                    # Check if it's below the label (within tolerance)
                    y_diff = candidate.y - label_y
                    if 0 < y_diff <= y_tolerance:
                        # Check horizontal alignment (roughly same X position)
                        x_diff = abs(candidate.x - label_x)
                        if x_diff <= x_tolerance:
                            # Validate pattern if provided
                            if value_pattern:
                                if re.search(value_pattern, candidate.text):
                                    return candidate.text
                            else:
                                return candidate.text

        return None

    def find_value_right_of_label(
        self,
        blocks: List[TextBlock],
        label: str,
        x_min_distance: float = 10.0,
        y_tolerance: float = 5.0,
        value_pattern: Optional[str] = None
    ) -> Optional[str]:
        """
        Find a value positioned to the right of a label (same line).

        Args:
            blocks: List of text blocks
            label: Label text to search for (case-insensitive)
            x_min_distance: Minimum X distance to consider (to skip colon, etc.)
            y_tolerance: Maximum Y difference to consider same line
            value_pattern: Optional regex pattern the value must match

        Returns:
            Extracted value or None
        """
        label_lower = label.lower()

        for i, block in enumerate(blocks):
            if label_lower in block.text.lower():
                label_y = block.y
                label_x2 = block.x2  # Right edge of label

                # Look for values on the same line (similar Y)
                candidates = []
                for j in range(i + 1, len(blocks)):
                    candidate = blocks[j]

                    # Check if on same line
                    y_diff = abs(candidate.y - label_y)
                    if y_diff <= y_tolerance:
                        # Check if to the right
                        x_diff = candidate.x - label_x2
                        if x_diff >= x_min_distance:
                            candidates.append((candidate, x_diff))
                    elif candidate.y > label_y + y_tolerance:
                        # Moved to next line
                        break

                # Sort by X distance and pick closest
                if candidates:
                    candidates.sort(key=lambda c: c[1])
                    for candidate, _ in candidates:
                        # Validate pattern if provided
                        if value_pattern:
                            if re.search(value_pattern, candidate.text):
                                return candidate.text
                        else:
                            return candidate.text

        return None

    def find_all_matches(
        self,
        blocks: List[TextBlock],
        pattern: str,
        max_matches: int = 10
    ) -> List[Tuple[str, TextBlock]]:
        """
        Find all text blocks matching a regex pattern.

        Args:
            blocks: List of text blocks
            pattern: Regex pattern to match
            max_matches: Maximum number of matches to return

        Returns:
            List of (matched_text, TextBlock) tuples
        """
        matches = []
        for block in blocks:
            match = re.search(pattern, block.text, re.IGNORECASE)
            if match:
                matches.append((match.group(0), block))
                if len(matches) >= max_matches:
                    break
        return matches

    def extract_table_region(
        self,
        blocks: List[TextBlock],
        start_marker: str,
        end_marker: Optional[str] = None,
        y_min: Optional[float] = None,
        y_max: Optional[float] = None
    ) -> List[TextBlock]:
        """
        Extract text blocks in a table region.

        Args:
            blocks: List of text blocks
            start_marker: Text marking the start of the table
            end_marker: Optional text marking the end
            y_min: Minimum Y coordinate (if marker not found)
            y_max: Maximum Y coordinate (if marker not found)

        Returns:
            List of blocks within the table region
        """
        # Find start position
        start_y = y_min
        if start_marker:
            for block in blocks:
                if start_marker.lower() in block.text.lower():
                    start_y = block.y
                    break

        # Find end position
        end_y = y_max
        if end_marker:
            for block in blocks:
                if end_marker.lower() in block.text.lower() and block.y > (start_y or 0):
                    end_y = block.y
                    break

        # Filter blocks in region
        region_blocks = []
        for block in blocks:
            in_region = True
            if start_y is not None and block.y < start_y:
                in_region = False
            if end_y is not None and block.y > end_y:
                in_region = False
            if in_region:
                region_blocks.append(block)

        return region_blocks

    def group_by_y_position(
        self,
        blocks: List[TextBlock],
        tolerance: float = 5.0
    ) -> Dict[int, List[TextBlock]]:
        """
        Group blocks by Y position (same line).

        Args:
            blocks: List of text blocks
            tolerance: Y tolerance for grouping

        Returns:
            Dictionary mapping Y bucket to list of blocks
        """
        groups = {}
        for block in blocks:
            y_key = int(block.y / tolerance) * int(tolerance)
            if y_key not in groups:
                groups[y_key] = []
            groups[y_key].append(block)

        # Sort each group by X position
        for y_key in groups:
            groups[y_key].sort(key=lambda b: b.x)

        return groups

    def extract_amount(self, text: str) -> Optional[float]:
        """
        Extract and normalize currency amount from text.

        Args:
            text: Text containing amount

        Returns:
            Normalized float value or None
        """
        try:
            # Remove currency symbols and whitespace
            cleaned = re.sub(r'[₹$€£Rs\.INR,\s]', '', text)

            # Handle negative amounts in parentheses
            negative = False
            if cleaned.startswith('(') and cleaned.endswith(')'):
                negative = True
                cleaned = cleaned[1:-1]

            # Handle CR/DR notation
            if 'CR' in text.upper():
                negative = False
            elif 'DR' in text.upper() or 'DB' in text.upper():
                negative = True

            # Extract numeric value
            match = re.search(r'[\d]+\.?\d{0,2}', cleaned)
            if match:
                value = float(match.group(0))
                return -value if negative else value
        except:
            pass

        return None

    def normalize_date(self, date_str: str) -> Optional[str]:
        """
        Normalize date string to YYYY-MM-DD format.

        Args:
            date_str: Date string in various formats

        Returns:
            Normalized date string or None
        """
        from app.utils.date_parser import parse_date
        try:
            parsed = parse_date(date_str)
            if parsed:
                return parsed.strftime("%Y-%m-%d")
        except:
            pass
        return None
