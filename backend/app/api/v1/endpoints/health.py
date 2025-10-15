"""Health check endpoint."""
from datetime import datetime
from fastapi import APIRouter
from app.models.schemas.response import HealthCheckResponse
from app.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return HealthCheckResponse(
        status="healthy",
        version=settings.VERSION,
        app_name=settings.APP_NAME,
        timestamp=datetime.utcnow().isoformat()
    )
