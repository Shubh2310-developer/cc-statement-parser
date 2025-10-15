"""Anomaly detection in extracted data."""
from typing import List
from dataclasses import dataclass

from app.models.domain.extraction_result import ExtractionResult
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Anomaly:
    field: str
    description: str
    severity: str  # low, medium, high


class AnomalyDetector:
    """Detect anomalies in extraction results."""

    def detect_anomalies(self, result: ExtractionResult) -> List[Anomaly]:
        """
        Detect anomalies.

        Args:
            result: Extraction result

        Returns:
            List of detected anomalies
        """
        anomalies = []

        # Check for extremely low confidence
        for field in result.fields.values():
            if field.confidence < 0.5:
                anomalies.append(Anomaly(
                    field=field.field_type.value,
                    description=f"Low confidence ({field.confidence:.2f})",
                    severity="medium"
                ))

        # Check for missing critical fields
        critical_fields = result.get_low_confidence_fields(threshold=0.7)
        if len(critical_fields) > 3:
            anomalies.append(Anomaly(
                field="overall",
                description=f"{len(critical_fields)} fields have low confidence",
                severity="high"
            ))

        logger.debug(f"Detected {len(anomalies)} anomalies")
        return anomalies
