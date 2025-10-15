"""Document repository."""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.database.models import DocumentModel
from app.models.domain.document import Document


class DocumentRepository(BaseRepository[DocumentModel]):
    """Repository for document operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(DocumentModel, session)

    async def create_document(self, job_id: str, document: Document, storage_path: str) -> DocumentModel:
        """Create document from domain model."""
        return await self.create(
            job_id=job_id,
            filename=document.filename,
            file_hash=document.file_hash,
            file_size=document.file_size,
            storage_path=storage_path,
            issuer=document.issuer.value if document.issuer else None
        )

    async def get_by_job_id(self, job_id: str) -> Optional[DocumentModel]:
        """Get document by job_id."""
        result = await self.session.execute(
            select(DocumentModel).where(DocumentModel.job_id == job_id)
        )
        return result.scalar_one_or_none()
