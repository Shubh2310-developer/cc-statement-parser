"""Text extraction module using PyMuPDF and pdfplumber.

This module handles text extraction from PDF documents with coordinate information
for spatial analysis. It supports multi-page PDFs and can detect scanned documents.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Import PyMuPDF - avoid conflict with frontend directory
try:
    import pymupdf as fitz
except ImportError:
    import fitz
import pdfplumber

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class TextBlock:
    """Represents a text block with position information."""

    text: str
    x0: float  # Left coordinate
    y0: float  # Top coordinate
    x1: float  # Right coordinate
    y1: float  # Bottom coordinate
    page_num: int
    confidence: float = 1.0

    @property
    def bbox(self) -> Tuple[float, float, float, float]:
        """Return bounding box as tuple."""
        return (self.x0, self.y0, self.x1, self.y1)

    @property
    def width(self) -> float:
        """Return width of text block."""
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        """Return height of text block."""
        return self.y1 - self.y0


@dataclass
class PageText:
    """Text extracted from a single page."""

    page_num: int
    full_text: str
    blocks: List[TextBlock]
    width: float
    height: float

    def get_text_density(self) -> float:
        """Calculate text density on page."""
        if not self.full_text:
            return 0.0
        page_area = self.width * self.height
        if page_area == 0:
            return 0.0
        return len(self.full_text) / page_area


@dataclass
class ExtractedText:
    """Complete text extraction result."""

    pages: List[PageText]
    total_pages: int
    is_scanned: bool
    total_text_length: int

    def get_full_text(self) -> str:
        """Get all text concatenated."""
        return "\n\n".join([page.full_text for page in self.pages])

    def get_page_text(self, page_num: int) -> Optional[str]:
        """Get text from specific page."""
        for page in self.pages:
            if page.page_num == page_num:
                return page.full_text
        return None


class TextExtractor:
    """Extract text from PDF documents with spatial information."""

    def __init__(self):
        """Initialize text extractor."""
        self.settings = get_settings()
        self.ocr_text_threshold = self.settings.OCR_TEXT_THRESHOLD

    def extract(self, pdf_bytes: bytes) -> ExtractedText:
        """Extract text from PDF using both PyMuPDF and pdfplumber.

        Args:
            pdf_bytes: PDF file content as bytes

        Returns:
            ExtractedText object with all extracted text and metadata

        Raises:
            ValueError: If PDF is invalid or corrupted
        """
        logger.info(f"Extracting text from PDF bytes")

        try:
            # Try PyMuPDF first (faster)
            pages = self._extract_with_pymupdf(pdf_bytes)

            # If PyMuPDF yields low text, try pdfplumber
            total_text = sum(len(page.full_text) for page in pages)
            if total_text < self.ocr_text_threshold:
                logger.info("Low text content with PyMuPDF, trying pdfplumber")
                pages_plumber = self._extract_with_pdfplumber(pdf_bytes)
                total_text_plumber = sum(len(page.full_text) for page in pages_plumber)

                # Use whichever extracted more text
                if total_text_plumber > total_text:
                    pages = pages_plumber
                    total_text = total_text_plumber

            is_scanned = total_text < self.ocr_text_threshold

            result = ExtractedText(
                pages=pages,
                total_pages=len(pages),
                is_scanned=is_scanned,
                total_text_length=total_text
            )

            logger.info(
                f"Extracted {total_text} characters from {len(pages)} pages. "
                f"Scanned: {is_scanned}"
            )

            return result

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise ValueError(f"Failed to extract text from PDF: {e}")

    def _extract_with_pymupdf(self, pdf_bytes: bytes) -> List[PageText]:
        """Extract text using PyMuPDF with coordinate information.

        Args:
            pdf_bytes: PDF file content as bytes

        Returns:
            List of PageText objects
        """
        pages = []

        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")

            for page_num in range(len(doc)):
                page = doc[page_num]

                # Get page dimensions
                rect = page.rect
                page_width = rect.width
                page_height = rect.height

                # Extract text blocks with positions
                blocks = []
                text_dict = page.get_text("dict")

                full_text_parts = []

                for block in text_dict.get("blocks", []):
                    if block.get("type") == 0:  # Text block
                        block_text_parts = []

                        for line in block.get("lines", []):
                            line_text = ""
                            for span in line.get("spans", []):
                                line_text += span.get("text", "")

                            if line_text.strip():
                                block_text_parts.append(line_text)

                        block_text = " ".join(block_text_parts)

                        if block_text.strip():
                            text_block = TextBlock(
                                text=block_text,
                                x0=block["bbox"][0],
                                y0=block["bbox"][1],
                                x1=block["bbox"][2],
                                y1=block["bbox"][3],
                                page_num=page_num + 1
                            )
                            blocks.append(text_block)
                            full_text_parts.append(block_text)

                # Also get simple text extraction as fallback
                simple_text = page.get_text()
                full_text = "\n".join(full_text_parts) if full_text_parts else simple_text

                page_text = PageText(
                    page_num=page_num + 1,
                    full_text=full_text,
                    blocks=blocks,
                    width=page_width,
                    height=page_height
                )
                pages.append(page_text)

            doc.close()

        except Exception as e:
            logger.error(f"PyMuPDF extraction failed: {e}")
            raise

        return pages

    def _extract_with_pdfplumber(self, pdf_bytes: bytes) -> List[PageText]:
        """Extract text using pdfplumber (better for some PDFs).

        Args:
            pdf_bytes: PDF file content as bytes

        Returns:
            List of PageText objects
        """
        pages = []

        try:
            import io
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Get page dimensions
                    page_width = float(page.width)
                    page_height = float(page.height)

                    # Extract text with positions
                    blocks = []
                    words = page.extract_words()

                    if words:
                        # Group words into lines based on y-coordinate
                        lines = self._group_words_into_lines(words)

                        for line_words in lines:
                            if not line_words:
                                continue

                            line_text = " ".join([w["text"] for w in line_words])

                            # Calculate bounding box for the line
                            x0 = min(w["x0"] for w in line_words)
                            y0 = min(w["top"] for w in line_words)
                            x1 = max(w["x1"] for w in line_words)
                            y1 = max(w["bottom"] for w in line_words)

                            text_block = TextBlock(
                                text=line_text,
                                x0=x0,
                                y0=y0,
                                x1=x1,
                                y1=y1,
                                page_num=page_num + 1
                            )
                            blocks.append(text_block)

                    # Get full text
                    full_text = page.extract_text() or ""

                    page_text = PageText(
                        page_num=page_num + 1,
                        full_text=full_text,
                        blocks=blocks,
                        width=page_width,
                        height=page_height
                    )
                    pages.append(page_text)

        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {e}")
            raise

        return pages

    def _group_words_into_lines(
        self,
        words: List[Dict],
        tolerance: float = 3.0
    ) -> List[List[Dict]]:
        """Group words into lines based on vertical position.

        Args:
            words: List of word dictionaries from pdfplumber
            tolerance: Vertical tolerance for grouping words into same line

        Returns:
            List of lines, where each line is a list of words
        """
        if not words:
            return []

        # Sort words by vertical position, then horizontal
        sorted_words = sorted(words, key=lambda w: (w["top"], w["x0"]))

        lines = []
        current_line = [sorted_words[0]]
        current_y = sorted_words[0]["top"]

        for word in sorted_words[1:]:
            # If word is on same line (within tolerance)
            if abs(word["top"] - current_y) <= tolerance:
                current_line.append(word)
            else:
                # Start new line
                lines.append(current_line)
                current_line = [word]
                current_y = word["top"]

        # Add last line
        if current_line:
            lines.append(current_line)

        return lines

    def get_text_in_region(
        self,
        extracted_text: ExtractedText,
        page_num: int,
        x0: float,
        y0: float,
        x1: float,
        y1: float
    ) -> str:
        """Get text within a specific region on a page.

        Args:
            extracted_text: ExtractedText object
            page_num: Page number (1-indexed)
            x0, y0, x1, y1: Bounding box coordinates

        Returns:
            Text within the specified region
        """
        text_parts = []

        for page in extracted_text.pages:
            if page.page_num != page_num:
                continue

            for block in page.blocks:
                # Check if block overlaps with region
                if self._boxes_overlap(
                    (block.x0, block.y0, block.x1, block.y1),
                    (x0, y0, x1, y1)
                ):
                    text_parts.append(block.text)

        return " ".join(text_parts)

    def _boxes_overlap(
        self,
        box1: Tuple[float, float, float, float],
        box2: Tuple[float, float, float, float]
    ) -> bool:
        """Check if two bounding boxes overlap.

        Args:
            box1: First box (x0, y0, x1, y1)
            box2: Second box (x0, y0, x1, y1)

        Returns:
            True if boxes overlap
        """
        x0_1, y0_1, x1_1, y1_1 = box1
        x0_2, y0_2, x1_2, y1_2 = box2

        # Check if boxes don't overlap (then negate)
        return not (x1_1 < x0_2 or x1_2 < x0_1 or y1_1 < y0_2 or y1_2 < y0_1)
