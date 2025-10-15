"""SQLAlchemy ORM models."""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class JobModel(Base):
    """Job database model."""
    
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(36), unique=True, nullable=False, index=True)
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)
    job_metadata = Column("metadata", JSON, default={})
    progress = Column(Integer, default=0)

    # Relationships
    document = relationship("DocumentModel", back_populates="job", uselist=False)
    result = relationship("ResultModel", back_populates="job", uselist=False)


class DocumentModel(Base):
    """Document database model."""
    
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(36), ForeignKey("jobs.job_id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=False)
    file_size = Column(Integer, nullable=False)
    storage_path = Column(String(512), nullable=False)
    issuer = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    job = relationship("JobModel", back_populates="document")


class ResultModel(Base):
    """Result database model."""
    
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(36), ForeignKey("jobs.job_id"), nullable=False, unique=True, index=True)
    extraction_result = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    job = relationship("JobModel", back_populates="result")
