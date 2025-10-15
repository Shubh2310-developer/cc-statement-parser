"""Document issuer classification."""
from dataclasses import dataclass
from typing import Optional

from app.core.extraction.text_extractor import TextExtractor
from app.models.enums import IssuerType
from app.models.schemas.internal import IssuerDetectionResult
from app.utils.logger import get_logger

logger = get_logger(__name__)


class IssuerClassifier:
    """Classify credit card statement issuer."""

    def __init__(self):
        self.text_extractor = TextExtractor()

    def classify_issuer(self, pdf_bytes: bytes) -> IssuerDetectionResult:
        """
        Classify the issuer from PDF content.

        Args:
            pdf_bytes: PDF file bytes

        Returns:
            IssuerDetectionResult with issuer and confidence
        """
        logger.info("Classifying document issuer")

        # Extract text from first 2 pages
        extracted = self.text_extractor.extract(pdf_bytes)
        text = "\n".join([p.full_text for p in extracted.pages[:2]])

        # Check for each issuer
        results = {}
        
        # HDFC
        if self._contains_any(text, ["HDFC Bank", "hdfcbank.com"]):
            results[IssuerType.HDFC] = 0.95
        
        # ICICI
        if self._contains_any(text, ["ICICI Bank", "icicibank.com", "L65190GJ1994PLC021012"]):
            results[IssuerType.ICICI] = 0.95
        
        # Axis
        if self._contains_any(text, ["Axis Bank", "axisbank.com", "MY ZONE"]):
            results[IssuerType.AXIS] = 0.95
        
        # SBI - Check first with higher confidence since it has unique markers
        if self._contains_any(text, ["SBI Card", "sbicard.com", "GSTIN of SBI Card"]):
            results[IssuerType.SBI] = 0.96

        # Amex - More specific pattern to avoid false matches
        if self._contains_any(text, ["American Express Company", "Membership Number", "Membership Rewards"]) or \
           (self._contains_any(text, ["AMEX"]) and not self._contains_any(text, ["SBI Card"])):
            results[IssuerType.AMEX] = 0.95

        if results:
            issuer = max(results, key=results.get)
            confidence = results[issuer]
            logger.info(f"Detected issuer: {issuer.value} (confidence: {confidence:.2f})")
            return IssuerDetectionResult(
                issuer=issuer,
                confidence=confidence,
                detection_method="text_pattern_matching"
            )

        logger.warning("Could not classify issuer")
        return IssuerDetectionResult(
            issuer=None,
            confidence=0.0,
            detection_method="text_pattern_matching"
        )

    def _contains_any(self, text: str, patterns: list) -> bool:
        """Check if text contains any of the patterns."""
        text_lower = text.lower()
        return any(p.lower() in text_lower for p in patterns)
