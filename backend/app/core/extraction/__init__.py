"""Extraction module for PDF data extraction.

This module provides comprehensive PDF extraction capabilities including:
- Text extraction with PyMuPDF and pdfplumber
- OCR for scanned documents with pytesseract
- Table extraction with Camelot
- Layout analysis for spatial understanding
- Field mapping to coordinate extraction
"""

from app.core.extraction.text_extractor import (
    TextExtractor,
    TextBlock,
    PageText,
    ExtractedText
)
from app.core.extraction.ocr_engine import (
    OCREngine,
    OCRResult,
    OCRPageResult
)
from app.core.extraction.table_extractor import (
    TableExtractor,
    TransactionRow,
    ExtractedTable,
    TableExtractionResult
)
from app.core.extraction.layout_analyzer import (
    LayoutAnalyzer,
    FieldLocation,
    LayoutRegion,
    LayoutAnalysisResult
)
from app.core.extraction.field_mapper import (
    FieldMapper,
    ExtractedField,
    StatementFields
)

__all__ = [
    # Text extraction
    'TextExtractor',
    'TextBlock',
    'PageText',
    'ExtractedText',

    # OCR
    'OCREngine',
    'OCRResult',
    'OCRPageResult',

    # Table extraction
    'TableExtractor',
    'TransactionRow',
    'ExtractedTable',
    'TableExtractionResult',

    # Layout analysis
    'LayoutAnalyzer',
    'FieldLocation',
    'LayoutRegion',
    'LayoutAnalysisResult',

    # Field mapping
    'FieldMapper',
    'ExtractedField',
    'StatementFields',
]
