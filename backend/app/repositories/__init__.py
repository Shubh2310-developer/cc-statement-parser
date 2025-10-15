"""Repositories module."""
from app.repositories.base import BaseRepository
from app.repositories.job_repository import JobRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.result_repository import ResultRepository

__all__ = [
    'BaseRepository',
    'JobRepository',
    'DocumentRepository',
    'ResultRepository',
]
