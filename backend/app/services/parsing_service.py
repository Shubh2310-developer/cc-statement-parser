"""Main parsing service orchestrating the entire process."""
from typing import Optional
from datetime import datetime

from app.core.extraction.orchestrator import ExtractionOrchestrator
from app.core.document.ingestion import DocumentIngestion
from app.storage.local_storage import LocalStorage
from app.repositories.job_repository import JobRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.result_repository import ResultRepository
from app.models.domain.job import Job
from app.models.enums import JobStatus
from app.models.schemas.request import ParseRequest
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ParsingService:
    """Main service for parsing credit card statements."""

    def __init__(
        self,
        job_repo: JobRepository,
        doc_repo: DocumentRepository,
        result_repo: ResultRepository
    ):
        self.job_repo = job_repo
        self.doc_repo = doc_repo
        self.result_repo = result_repo
        self.orchestrator = ExtractionOrchestrator()
        self.ingestion = DocumentIngestion()
        self.storage = LocalStorage()

    async def parse_document(
        self,
        file_bytes: bytes,
        filename: str,
        options: Optional[ParseRequest] = None
    ) -> str:
        """
        Parse credit card statement.

        Args:
            file_bytes: PDF file content
            filename: Original filename
            options: Optional parsing options

        Returns:
            Job ID for tracking

        Raises:
            Various exceptions on failure
        """
        logger.info(f"Starting parse for file: {filename}")

        # Create job
        job = Job(status=JobStatus.PENDING)
        job_model = await self.job_repo.create_job(job)
        job_id = job.id

        try:
            # Update to processing
            job.start()
            await self.job_repo.update_status(job_id, JobStatus.PROCESSING.value, progress=10)

            # Ingest document
            document = self.ingestion.ingest_file(file_bytes, filename)
            await self.job_repo.update_status(job_id, JobStatus.PROCESSING.value, progress=20)

            # Save to storage
            storage_path = await self.storage.save(job_id, file_bytes)
            await self.doc_repo.create_document(job_id, document, storage_path)
            await self.job_repo.update_status(job_id, JobStatus.PROCESSING.value, progress=30)

            # Extract fields
            logger.info(f"Starting extraction for job {job_id}")
            extraction_result = self.orchestrator.orchestrate(file_bytes, options)
            await self.job_repo.update_status(job_id, JobStatus.PROCESSING.value, progress=80)

            # Save result
            await self.result_repo.save_result(job_id, extraction_result.to_dict())
            await self.job_repo.update_status(job_id, JobStatus.PROCESSING.value, progress=95)

            # Complete job
            job.complete(result_id=job_id)
            await self.job_repo.update_status(
                job_id,
                JobStatus.COMPLETED.value,
                progress=100,
                completed_at=datetime.utcnow()
            )

            logger.info(f"Parse completed successfully for job {job_id}")
            return job_id

        except Exception as e:
            logger.error(f"Parse failed for job {job_id}: {e}", exc_info=True)
            job.fail(error_message=str(e))
            await self.job_repo.update_status(
                job_id,
                JobStatus.FAILED.value,
                error=str(e)
            )
            raise
