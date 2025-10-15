"""Parse endpoint for file upload."""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db_session
from app.services.parsing_service import ParsingService
from app.repositories.job_repository import JobRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.result_repository import ResultRepository
from app.models.schemas.response import UploadResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/parse", response_model=UploadResponse)
async def parse_statement(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Upload and parse credit card statement.

    Args:
        file: PDF file upload
        session: Database session

    Returns:
        Upload response with job_id
    """
    logger.info(f"Received file upload: {file.filename}")

    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        # Read file content
        file_bytes = await file.read()

        # Create service
        parsing_service = ParsingService(
            JobRepository(session),
            DocumentRepository(session),
            ResultRepository(session)
        )

        # Parse document
        job_id = await parsing_service.parse_document(file_bytes, file.filename)

        return UploadResponse(
            document_id="",  # Will be populated after processing
            job_id=job_id,
            message="File uploaded and processing started"
        )

    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
