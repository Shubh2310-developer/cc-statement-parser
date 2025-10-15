"""Main extraction orchestrator that coordinates the entire parsing pipeline."""
from typing import Optional
from dataclasses import dataclass

from app.core.document.classifier import IssuerClassifier
from app.core.document.preprocessor import DocumentPreprocessor
from app.core.document.quality_checker import QualityChecker
from app.core.extraction.field_mapper import FieldMapper
from app.core.parsers.factory import ParserFactory
from app.core.validation.schema_validator import SchemaValidator
from app.core.validation.confidence_scorer import ConfidenceScorer
from app.core.validation.business_rules import BusinessRulesValidator
from app.models.domain.extraction_result import ExtractionResult
from app.models.enums import IssuerType
from app.models.schemas.request import ParseRequest
from app.utils.logger import get_logger
from app.utils.exceptions import ParsingError

logger = get_logger(__name__)


class ExtractionOrchestrator:
    """Orchestrate the complete extraction pipeline."""

    def __init__(self):
        self.classifier = IssuerClassifier()
        self.preprocessor = DocumentPreprocessor()
        self.quality_checker = QualityChecker()
        self.field_mapper = FieldMapper()
        self.schema_validator = SchemaValidator()
        self.confidence_scorer = ConfidenceScorer()
        self.business_validator = BusinessRulesValidator()

    def orchestrate(
        self,
        pdf_bytes: bytes,
        options: Optional[ParseRequest] = None
    ) -> ExtractionResult:
        """
        Orchestrate the complete extraction pipeline.

        Pipeline:
        1. Preprocess PDF
        2. Check quality
        3. Classify issuer
        4. Select parser
        5. Extract fields
        6. Validate results
        7. Score confidence

        Args:
            pdf_bytes: PDF file content
            options: Optional parsing options

        Returns:
            Complete ExtractionResult

        Raises:
            ParsingError: If extraction fails
        """
        logger.info("Starting extraction orchestration")

        try:
            # Step 1: Preprocess
            logger.debug("Step 1: Preprocessing PDF")
            processed_bytes = self.preprocessor.preprocess(pdf_bytes)

            # Step 2: Check quality
            logger.debug("Step 2: Checking quality")
            quality_score = self.quality_checker.check_quality(processed_bytes)
            logger.info(f"PDF quality score: {quality_score:.2f}")

            # Step 3: Classify issuer
            logger.debug("Step 3: Classifying issuer")
            issuer_hint = options.issuer_hint if options else None
            
            if not issuer_hint:
                detection = self.classifier.classify_issuer(processed_bytes)
                issuer_hint = detection.issuer
                logger.info(f"Detected issuer: {issuer_hint.value if issuer_hint else 'Unknown'}")

            # Step 4: Select parser
            logger.debug("Step 4: Selecting parser")
            parser = ParserFactory.get_parser(processed_bytes, issuer_hint)
            logger.info(f"Selected parser: {parser.__class__.__name__}")

            # Step 5: Extract fields with hybrid approach
            logger.debug("Step 5: Extracting fields")
            
            # First use FieldMapper for general extraction
            from app.core.extraction.text_extractor import TextExtractor
            text_extractor = TextExtractor()
            extracted_text = text_extractor.extract(processed_bytes)
            full_text = "\n".join([p.full_text for p in extracted_text.pages])
            
            # Use field mapper
            statement_fields = self.field_mapper.extract_fields(processed_bytes)

            # Then use bank-specific parser for refinement
            # Pass PDF bytes for spatial-aware parsers
            if hasattr(parser, 'parse_with_pdf'):
                result = parser.parse_with_pdf(processed_bytes, full_text, statement_fields)
            else:
                result = parser.parse(full_text, statement_fields)
            
            # Add metadata
            result.extraction_metadata["quality_score"] = quality_score
            result.extraction_metadata["page_count"] = extracted_text.total_pages
            result.extraction_metadata["parser_used"] = parser.__class__.__name__

            # Step 6: Validate
            logger.debug("Step 6: Validating results")
            validation = self.schema_validator.validate(result)
            result.validation_errors = validation.errors

            # Business rules
            business_errors = self.business_validator.validate_business_rules(result)
            if business_errors:
                result.validation_errors.extend(business_errors)

            # Step 7: Score confidence
            logger.debug("Step 7: Scoring confidence")
            overall_confidence = self.confidence_scorer.calculate_overall_confidence(result)
            result.overall_confidence = overall_confidence

            logger.info(
                f"Extraction complete: "
                f"{result.field_count} fields, "
                f"confidence={overall_confidence:.2f}, "
                f"errors={len(result.validation_errors)}"
            )

            return result

        except Exception as e:
            logger.error(f"Orchestration failed: {e}", exc_info=True)
            raise ParsingError("Extraction pipeline failed", details=str(e)) from e
