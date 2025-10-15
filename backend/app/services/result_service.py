"""Result retrieval service."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.result_repository import ResultRepository
from app.models.domain.extraction_result import ExtractionResult
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ResultService:
    """Service for result retrieval."""

    def __init__(self, session: AsyncSession):
        self.result_repo = ResultRepository(session)

    async def get_result(self, job_id: str) -> Optional[dict]:
        """
        Get extraction result by job ID.

        Args:
            job_id: Job identifier

        Returns:
            Extraction result dictionary or None
        """
        logger.debug(f"Getting result for job: {job_id}")
        result_model = await self.result_repo.get_by_job_id(job_id)
        
        if not result_model:
            return None

        return result_model.extraction_result
