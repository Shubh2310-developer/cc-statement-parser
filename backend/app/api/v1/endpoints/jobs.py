"""Job management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any

from app.database.connection import get_db_session
from app.services.job_service import JobService
from app.services.result_service import ResultService
from app.models.schemas.response import JobResponse, MessageResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/jobs/{job_id}")
async def get_job_status(
    job_id: str = Path(..., description="Job ID"),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Get job status with result if available.

    Args:
        job_id: Job identifier
        session: Database session

    Returns:
        Job status response with result
    """
    logger.debug(f"Getting status for job: {job_id}")

    job_service = JobService(session)
    job = await job_service.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get result if job is completed
    result_data: Optional[Dict[Any, Any]] = None
    if job.status.value == "completed":
        result_service = ResultService(session)
        result = await result_service.get_result(job_id)
        if result:
            result_data = result

    response = {
        "id": job.id,
        "document_id": job.document_id or "",
        "status": job.status.value,
        "progress": job.progress or 0,
        "created_at": job.created_at.isoformat(),
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "error_message": job.error_message,
        "result": result_data
    }

    return response


@router.delete("/jobs/{job_id}", response_model=MessageResponse)
async def cancel_job(
    job_id: str = Path(..., description="Job ID"),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Cancel/delete job.

    Args:
        job_id: Job identifier
        session: Database session

    Returns:
        Success message
    """
    logger.info(f"Cancelling job: {job_id}")

    job_service = JobService(session)
    deleted = await job_service.delete_job(job_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Job not found")

    return MessageResponse(
        message="Job cancelled successfully",
        status="success"
    )
