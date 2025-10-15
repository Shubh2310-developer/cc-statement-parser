"""Main API router aggregating all endpoints."""
from fastapi import APIRouter

from app.api.v1.endpoints import parse, jobs, health

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(parse.router, tags=["parse"])
api_router.include_router(jobs.router, tags=["jobs"])
api_router.include_router(health.router, tags=["health"])

# Results endpoint
from fastapi import Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db_session
from app.services.result_service import ResultService
from app.models.schemas.response import ExtractionResultResponse


@api_router.get("/results/{job_id}", response_model=ExtractionResultResponse, tags=["results"])
async def get_results(
    job_id: str = Path(..., description="Job ID"),
    session: AsyncSession = Depends(get_db_session)
):
    """Get extraction results for a job."""
    result_service = ResultService(session)
    result = await result_service.get_result(job_id)

    if not result:
        raise HTTPException(status_code=404, detail="Results not found")

    return ExtractionResultResponse(
        job_id=job_id,
        data=result
    )
