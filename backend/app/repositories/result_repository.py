"""Result repository."""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.database.models import ResultModel


class ResultRepository(BaseRepository[ResultModel]):
    """Repository for result operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(ResultModel, session)

    async def save_result(self, job_id: str, extraction_result: dict) -> ResultModel:
        """Save extraction result."""
        return await self.create(
            job_id=job_id,
            extraction_result=extraction_result
        )

    async def get_by_job_id(self, job_id: str) -> Optional[ResultModel]:
        """Get result by job_id."""
        result = await self.session.execute(
            select(ResultModel).where(ResultModel.job_id == job_id)
        )
        return result.scalar_one_or_none()
