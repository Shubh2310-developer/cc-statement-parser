"""Job repository."""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.database.models import JobModel
from app.models.domain.job import Job


class JobRepository(BaseRepository[JobModel]):
    """Repository for job operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(JobModel, session)

    async def get_by_job_id(self, job_id: str) -> Optional[JobModel]:
        """Get job by job_id."""
        result = await self.session.execute(
            select(JobModel).where(JobModel.job_id == job_id)
        )
        return result.scalar_one_or_none()

    async def create_job(self, job: Job) -> JobModel:
        """Create job from domain model."""
        return await self.create(
            job_id=job.id,
            status=job.status.value,
            created_at=job.created_at,
            job_metadata=job.metadata,
            progress=job.progress
        )

    async def update_status(self, job_id: str, status: str, **kwargs) -> Optional[JobModel]:
        """Update job status."""
        job_model = await self.get_by_job_id(job_id)
        if job_model:
            job_model.status = status
            for key, value in kwargs.items():
                setattr(job_model, key, value)
            await self.session.commit()
            await self.session.refresh(job_model)
        return job_model
