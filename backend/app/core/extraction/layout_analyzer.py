"""Layout analysis module for spatial PDF analysis.

This module analyzes the spatial layout of PDF documents to find field values
near labels, calculate bounding boxes, and understand document structure.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict
import re

from app.config import get_settings
from app.core.extraction.text_extractor import TextBlock, ExtractedText, PageText

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class FieldLocation:
    """Location information for a field."""

    label: str
    value: str
    label_bbox: Tuple[float, float, float, float]
    value_bbox: Tuple[float, float, float, float]
    page_num: int
    confidence: float = 0.0


@dataclass
class LayoutRegion:
    """Represents a region in the document layout."""

    region_type: str  # 'header', 'footer', 'body', 'table', 'sidebar'
    bbox: Tuple[float, float, float, float]
    page_num: int
    blocks: List[TextBlock]

    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is within region."""
        x0, y0, x1, y1 = self.bbox
        return x0 <= x <= x1 and y0 <= y <= y1


@dataclass
class LayoutAnalysisResult:
    """Result of layout analysis."""

    regions: List[LayoutRegion]
    field_locations: List[FieldLocation]
    document_structure: Dict[str, Any]


class LayoutAnalyzer:
    """Analyze spatial layout of PDF documents."""

    def __init__(self):
        """Initialize layout analyzer."""
        self.settings = get_settings()

        # Common field labels to look for
        self.field_patterns = {
            'card_number': [
                r'card\s*(?:no|number|#)',
                r'credit\s*card\s*(?:no|number)',
                r'account\s*(?:no|number)'
            ],
            'card_holder': [
                r'(?:card\s*)?holder\s*name',
                r'name\s*on\s*card',
                r'cardholder'
            ],
            'statement_date': [
                r'statement\s*date',
                r'billing\s*date',
                r'as\s*(?:of|on)'
            ],
            'due_date': [
                r'(?:payment\s*)?due\s*date',
                r'pay\s*by',
                r'payment\s*deadline'
            ],
            'minimum_due': [
                r'minimum\s*(?:amount\s*)?due',
                r'minimum\s*payment',
                r'min(?:imum)?\s*due'
            ],
            'total_due': [
                r'total\s*(?:amount\s*)?due',
                r'total\s*balance',
                r'amount\s*due',
                r'outstanding\s*balance'
            ],
            'credit_limit': [
                r'credit\s*limit',
                r'(?:total\s*)?limit',
                r'available\s*credit'
            ],
            'opening_balance': [
                r'opening\s*balance',
                r'previous\s*balance',
                r'balance\s*(?:brought\s*)?forward'
            ],
            'closing_balance': [
                r'closing\s*balance',
                r'new\s*balance',
                r'current\s*balance'
            ]
        }

    def analyze_layout(
        self,
        extracted_text: ExtractedText
    ) -> LayoutAnalysisResult:
        """Analyze document layout and identify field locations.

        Args:
            extracted_text: ExtractedText object from text extraction

        Returns:
            LayoutAnalysisResult with spatial analysis
        """
        logger.info("Analyzing document layout")

        # Identify regions
        regions = self._identify_regions(extracted_text)

        # Find field locations
        field_locations = self._find_field_locations(extracted_text)

        # Build document structure
        document_structure = self._build_document_structure(
            extracted_text,
            regions,
            field_locations
        )

        result = LayoutAnalysisResult(
            regions=regions,
            field_locations=field_locations,
            document_structure=document_structure
        )

        logger.info(
            f"Layout analysis complete: {len(regions)} regions, "
            f"{len(field_locations)} fields found"
        )

        return result

    def _identify_regions(
        self,
        extracted_text: ExtractedText
    ) -> List[LayoutRegion]:
        """Identify different regions in the document.

        Args:
            extracted_text: ExtractedText object

        Returns:
            List of LayoutRegion objects
        """
        regions = []

        for page in extracted_text.pages:
            # Identify header (top 15% of page)
            header_blocks = [
                block for block in page.blocks
                if block.y0 < page.height * 0.15
            ]
            if header_blocks:
                regions.append(LayoutRegion(
                    region_type='header',
                    bbox=self._calculate_bounding_box(header_blocks),
                    page_num=page.page_num,
                    blocks=header_blocks
                ))

            # Identify footer (bottom 10% of page)
            footer_blocks = [
                block for block in page.blocks
                if block.y1 > page.height * 0.90
            ]
            if footer_blocks:
                regions.append(LayoutRegion(
                    region_type='footer',
                    bbox=self._calculate_bounding_box(footer_blocks),
                    page_num=page.page_num,
                    blocks=footer_blocks
                ))

            # Body region (middle section)
            body_blocks = [
                block for block in page.blocks
                if page.height * 0.15 <= block.y0 <= page.height * 0.90
            ]
            if body_blocks:
                regions.append(LayoutRegion(
                    region_type='body',
                    bbox=self._calculate_bounding_box(body_blocks),
                    page_num=page.page_num,
                    blocks=body_blocks
                ))

        return regions

    def _find_field_locations(
        self,
        extracted_text: ExtractedText
    ) -> List[FieldLocation]:
        """Find locations of labeled fields in the document.

        Args:
            extracted_text: ExtractedText object

        Returns:
            List of FieldLocation objects
        """
        field_locations = []

        for page in extracted_text.pages:
            for field_name, patterns in self.field_patterns.items():
                location = self._find_field_on_page(page, field_name, patterns)
                if location:
                    field_locations.append(location)

        return field_locations

    def _find_field_on_page(
        self,
        page: PageText,
        field_name: str,
        patterns: List[str]
    ) -> Optional[FieldLocation]:
        """Find a specific field on a page.

        Args:
            page: PageText object
            field_name: Name of field to find
            patterns: List of regex patterns to match label

        Returns:
            FieldLocation object or None
        """
        # Search for label in text blocks
        for i, block in enumerate(page.blocks):
            block_text = block.text.lower()

            # Check if any pattern matches
            for pattern in patterns:
                if re.search(pattern, block_text, re.IGNORECASE):
                    # Found label, now find value
                    value_block = self._find_value_near_label(
                        block,
                        page.blocks,
                        i
                    )

                    if value_block:
                        return FieldLocation(
                            label=field_name,
                            value=value_block.text,
                            label_bbox=block.bbox,
                            value_bbox=value_block.bbox,
                            page_num=page.page_num,
                            confidence=0.8
                        )

        return None

    def _find_value_near_label(
        self,
        label_block: TextBlock,
        all_blocks: List[TextBlock],
        label_index: int
    ) -> Optional[TextBlock]:
        """Find value block near a label block.

        Args:
            label_block: The label TextBlock
            all_blocks: All text blocks on page
            label_index: Index of label block in all_blocks

        Returns:
            TextBlock containing value or None
        """
        # Strategy 1: Value on same line to the right
        candidates = []

        for block in all_blocks:
            if block == label_block:
                continue

            # Check if on same line (similar y-coordinate)
            if abs(block.y0 - label_block.y0) < 10:
                # To the right of label
                if block.x0 > label_block.x1:
                    distance = block.x0 - label_block.x1
                    candidates.append((distance, block))

        # Also check next block (Strategy 2: Value on next line)
        if label_index + 1 < len(all_blocks):
            next_block = all_blocks[label_index + 1]
            # If it's below and relatively close
            if next_block.y0 > label_block.y0 and next_block.y0 - label_block.y1 < 20:
                candidates.append((0, next_block))

        # Return closest candidate
        if candidates:
            candidates.sort(key=lambda x: x[0])
            return candidates[0][1]

        return None

    def _calculate_bounding_box(
        self,
        blocks: List[TextBlock]
    ) -> Tuple[float, float, float, float]:
        """Calculate bounding box that encompasses all blocks.

        Args:
            blocks: List of TextBlock objects

        Returns:
            Bounding box tuple (x0, y0, x1, y1)
        """
        if not blocks:
            return (0, 0, 0, 0)

        x0 = min(block.x0 for block in blocks)
        y0 = min(block.y0 for block in blocks)
        x1 = max(block.x1 for block in blocks)
        y1 = max(block.y1 for block in blocks)

        return (x0, y0, x1, y1)

    def _build_document_structure(
        self,
        extracted_text: ExtractedText,
        regions: List[LayoutRegion],
        field_locations: List[FieldLocation]
    ) -> Dict[str, Any]:
        """Build structured representation of document.

        Args:
            extracted_text: ExtractedText object
            regions: List of regions
            field_locations: List of field locations

        Returns:
            Dictionary with document structure info
        """
        structure = {
            'total_pages': extracted_text.total_pages,
            'is_scanned': extracted_text.is_scanned,
            'pages': []
        }

        for page in extracted_text.pages:
            page_regions = [r for r in regions if r.page_num == page.page_num]
            page_fields = [f for f in field_locations if f.page_num == page.page_num]

            page_info = {
                'page_num': page.page_num,
                'dimensions': {
                    'width': page.width,
                    'height': page.height
                },
                'text_density': page.get_text_density(),
                'regions': [
                    {
                        'type': r.region_type,
                        'bbox': r.bbox,
                        'block_count': len(r.blocks)
                    }
                    for r in page_regions
                ],
                'fields': [
                    {
                        'label': f.label,
                        'value': f.value,
                        'confidence': f.confidence
                    }
                    for f in page_fields
                ],
                'block_count': len(page.blocks)
            }

            structure['pages'].append(page_info)

        return structure

    def find_text_near_coordinates(
        self,
        extracted_text: ExtractedText,
        page_num: int,
        x: float,
        y: float,
        radius: float = 50.0
    ) -> List[TextBlock]:
        """Find text blocks near specific coordinates.

        Args:
            extracted_text: ExtractedText object
            page_num: Page number (1-indexed)
            x, y: Coordinates
            radius: Search radius in points

        Returns:
            List of TextBlock objects within radius
        """
        results = []

        for page in extracted_text.pages:
            if page.page_num != page_num:
                continue

            for block in page.blocks:
                # Calculate center of block
                block_center_x = (block.x0 + block.x1) / 2
                block_center_y = (block.y0 + block.y1) / 2

                # Calculate distance
                distance = ((block_center_x - x) ** 2 + (block_center_y - y) ** 2) ** 0.5

                if distance <= radius:
                    results.append(block)

        return results

    def group_blocks_by_column(
        self,
        blocks: List[TextBlock],
        tolerance: float = 10.0
    ) -> List[List[TextBlock]]:
        """Group text blocks by column (vertical alignment).

        Args:
            blocks: List of TextBlock objects
            tolerance: Horizontal tolerance for grouping

        Returns:
            List of columns, each containing list of blocks
        """
        if not blocks:
            return []

        # Sort blocks by x-coordinate
        sorted_blocks = sorted(blocks, key=lambda b: b.x0)

        columns = []
        current_column = [sorted_blocks[0]]
        current_x = sorted_blocks[0].x0

        for block in sorted_blocks[1:]:
            # If block is in same column (x-coordinate within tolerance)
            if abs(block.x0 - current_x) <= tolerance:
                current_column.append(block)
            else:
                # Start new column
                columns.append(current_column)
                current_column = [block]
                current_x = block.x0

        # Add last column
        if current_column:
            columns.append(current_column)

        # Sort blocks within each column by y-coordinate
        for column in columns:
            column.sort(key=lambda b: b.y0)

        return columns

    def detect_table_regions(
        self,
        page: PageText,
        min_rows: int = 3
    ) -> List[Tuple[float, float, float, float]]:
        """Detect potential table regions based on layout.

        Args:
            page: PageText object
            min_rows: Minimum number of rows to consider as table

        Returns:
            List of bounding boxes for potential tables
        """
        # Group blocks by row
        rows = self._group_blocks_by_row(page.blocks)

        if len(rows) < min_rows:
            return []

        # Find consecutive rows with similar column structure
        table_regions = []
        current_table_rows = []

        for i, row in enumerate(rows):
            # Check if row has multiple columns
            if len(row) >= 2:
                current_table_rows.append(row)
            else:
                # End of potential table
                if len(current_table_rows) >= min_rows:
                    # Calculate bounding box for this table
                    all_blocks = [block for row in current_table_rows for block in row]
                    bbox = self._calculate_bounding_box(all_blocks)
                    table_regions.append(bbox)

                current_table_rows = []

        # Check if last set of rows forms a table
        if len(current_table_rows) >= min_rows:
            all_blocks = [block for row in current_table_rows for block in row]
            bbox = self._calculate_bounding_box(all_blocks)
            table_regions.append(bbox)

        return table_regions

    def _group_blocks_by_row(
        self,
        blocks: List[TextBlock],
        tolerance: float = 5.0
    ) -> List[List[TextBlock]]:
        """Group text blocks by row (horizontal alignment).

        Args:
            blocks: List of TextBlock objects
            tolerance: Vertical tolerance for grouping

        Returns:
            List of rows, each containing list of blocks
        """
        if not blocks:
            return []

        # Sort blocks by y-coordinate
        sorted_blocks = sorted(blocks, key=lambda b: b.y0)

        rows = []
        current_row = [sorted_blocks[0]]
        current_y = sorted_blocks[0].y0

        for block in sorted_blocks[1:]:
            # If block is in same row (y-coordinate within tolerance)
            if abs(block.y0 - current_y) <= tolerance:
                current_row.append(block)
            else:
                # Start new row
                rows.append(current_row)
                current_row = [block]
                current_y = block.y0

        # Add last row
        if current_row:
            rows.append(current_row)

        # Sort blocks within each row by x-coordinate
        for row in rows:
            row.sort(key=lambda b: b.x0)

        return rows

    def calculate_reading_order(
        self,
        blocks: List[TextBlock]
    ) -> List[TextBlock]:
        """Calculate natural reading order for text blocks.

        Args:
            blocks: List of TextBlock objects

        Returns:
            Blocks sorted in reading order (top-to-bottom, left-to-right)
        """
        # Group into rows first
        rows = self._group_blocks_by_row(blocks)

        # Flatten rows (they're already sorted internally)
        ordered_blocks = []
        for row in rows:
            ordered_blocks.extend(row)

        return ordered_blocks
