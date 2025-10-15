"""Dependency injection setup."""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db_session
from app.services.parsing_service import ParsingService
from app.services.job_service import JobService
from app.services.result_service import ResultService
from app.repositories.job_repository import JobRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.result_repository import ResultRepository


async def get_parsing_service(
    session: AsyncSession = Depends(get_db_session)
) -> ParsingService:
    """Get parsing service."""
    return ParsingService(
        JobRepository(session),
        DocumentRepository(session),
        ResultRepository(session)
    )


async def get_job_service(
    session: AsyncSession = Depends(get_db_session)
) -> JobService:
    """Get job service."""
    return JobService(session)


async def get_result_service(
    session: AsyncSession = Depends(get_db_session)
) -> ResultService:
    """Get result service."""
    return ResultService(session)
