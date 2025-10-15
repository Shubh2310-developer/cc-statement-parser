"""Job management service."""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.job_repository import JobRepository
from app.models.domain.job import Job
from app.models.enums import JobStatus
from app.utils.logger import get_logger
from app.utils.exceptions import DatabaseError

logger = get_logger(__name__)


class JobService:
    """Service for job management operations."""

    def __init__(self, session: AsyncSession):
        self.job_repo = JobRepository(session)

    async def get_job(self, job_id: str) -> Optional[Job]:
        """
        Get job by ID.

        Args:
            job_id: Job identifier

        Returns:
            Job domain model or None
        """
        logger.debug(f"Getting job: {job_id}")
        job_model = await self.job_repo.get_by_job_id(job_id)
        
        if not job_model:
            return None

        # Convert to domain model
        return Job(
            id=job_model.job_id,
            status=JobStatus(job_model.status),
            created_at=job_model.created_at,
            completed_at=job_model.completed_at,
            error_message=job_model.error,
            metadata=job_model.job_metadata or {},
            progress=job_model.progress
        )

    async def get_all_jobs(self, limit: int = 100) -> List[Job]:
        """Get all jobs."""
        logger.debug(f"Getting all jobs (limit: {limit})")
        job_models = await self.job_repo.get_all(limit)
        
        return [
            Job(
                id=jm.job_id,
                status=JobStatus(jm.status),
                created_at=jm.created_at,
                completed_at=jm.completed_at,
                error_message=jm.error,
                metadata=jm.job_metadata or {},
                progress=jm.progress
            )
            for jm in job_models
        ]

    async def delete_job(self, job_id: str) -> bool:
        """Delete job."""
        logger.info(f"Deleting job: {job_id}")
        job_model = await self.job_repo.get_by_job_id(job_id)
        if job_model:
            return await self.job_repo.delete(job_model.id)
        return False
