"""Parser factory for selecting the appropriate bank-specific parser."""
from typing import Optional, List
import io

from app.core.parsers.base import BaseParser
from app.core.parsers.hdfc_parser import HDFCParser
from app.core.parsers.icici_parser import ICICIParser
from app.core.parsers.axis_parser import AxisParser
from app.core.parsers.amex_parser import AmexParser
from app.core.parsers.sbi_parser import SBIParser
from app.core.extraction.text_extractor import TextExtractor
from app.models.enums import IssuerType
from app.utils.logger import get_logger
from app.utils.exceptions import IssuerNotSupportedError

logger = get_logger(__name__)


class ParserFactory:
    """Factory for creating appropriate parser based on document content."""

    # Registry of all available parsers
    _parsers: List[BaseParser] = [
        HDFCParser(),
        ICICIParser(),
        AxisParser(),
        AmexParser(),
        SBIParser(),
    ]

    @classmethod
    def get_parser(
        cls,
        pdf_bytes: bytes,
        issuer_hint: Optional[IssuerType] = None
    ) -> BaseParser:
        """
        Get the appropriate parser for the given PDF.

        Args:
            pdf_bytes: PDF file content
            issuer_hint: Optional hint about the issuer

        Returns:
            Appropriate BaseParser instance

        Raises:
            IssuerNotSupportedError: If no suitable parser found
        """
        logger.info("Selecting parser for document")

        # Extract text from PDF for classification
        try:
            text_extractor = TextExtractor()
            extracted = text_extractor.extract(pdf_bytes)
            
            # Use first page and some of second page for classification
            full_text = ""
            for i, page in enumerate(extracted.pages[:2]):
                full_text += page.full_text + "\n"
            
            logger.debug(f"Extracted {len(full_text)} characters for classification")
            
        except Exception as e:
            logger.error(f"Failed to extract text for classification: {e}")
            raise IssuerNotSupportedError("Could not extract text from PDF") from e

        # If issuer hint provided, try that parser first
        if issuer_hint:
            logger.info(f"Using issuer hint: {issuer_hint.value}")
            for parser in cls._parsers:
                if parser.get_issuer_type() == issuer_hint:
                    can_parse, confidence = parser.can_parse(full_text)
                    if can_parse:
                        logger.info(f"Matched {parser.__class__.__name__} (confidence: {confidence:.2f})")
                        return parser
                    else:
                        logger.warning(f"Issuer hint {issuer_hint.value} did not match document")

        # Try all parsers and select the one with highest confidence
        best_parser = None
        best_confidence = 0.0

        for parser in cls._parsers:
            try:
                can_parse, confidence = parser.can_parse(full_text)
                logger.debug(f"{parser.__class__.__name__}: can_parse={can_parse}, confidence={confidence:.2f}")
                
                if can_parse and confidence > best_confidence:
                    best_parser = parser
                    best_confidence = confidence
                    
            except Exception as e:
                logger.warning(f"Error checking {parser.__class__.__name__}: {e}")
                continue

        if best_parser and best_confidence >= 0.6:
            logger.info(f"Selected {best_parser.__class__.__name__} (confidence: {best_confidence:.2f})")
            return best_parser

        # No suitable parser found
        logger.error("No suitable parser found for document")
        raise IssuerNotSupportedError(
            "Could not identify credit card issuer. Supported issuers: HDFC, ICICI, Axis, Amex, SBI",
            details=f"Best confidence: {best_confidence:.2f}"
        )

    @classmethod
    def get_supported_issuers(cls) -> List[IssuerType]:
        """
        Get list of supported issuers.

        Returns:
            List of supported IssuerType values
        """
        return [parser.get_issuer_type() for parser in cls._parsers]

    @classmethod
    def register_parser(cls, parser: BaseParser):
        """
        Register a new parser.

        Args:
            parser: Parser instance to register
        """
        cls._parsers.append(parser)
        logger.info(f"Registered parser: {parser.__class__.__name__}")
