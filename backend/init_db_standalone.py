#!/usr/bin/env python3
"""Standalone database initialization script with no app dependencies."""
import asyncio
from pathlib import Path
from datetime import datetime

# Create database schema without importing from app
async def init_database():
    """Initialize database with raw SQL."""
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text

    # Database URL
    backend_dir = Path(__file__).parent
    db_path = backend_dir / "data" / "db" / "cc_parser.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    database_url = f"sqlite+aiosqlite:///{db_path}"

    print(f"Initializing database at: {db_path}")

    # Create engine
    engine = create_async_engine(database_url, echo=False)

    # Create tables with raw SQL
    async with engine.begin() as conn:
        # Create jobs table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                document_id TEXT,
                status TEXT NOT NULL,
                result_id TEXT,
                error_message TEXT,
                metadata TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
        """))

        # Create documents table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                file_hash TEXT NOT NULL,
                mime_type TEXT NOT NULL,
                is_scanned INTEGER NOT NULL,
                page_count INTEGER,
                uploaded_at TEXT NOT NULL,
                UNIQUE (file_hash)
            )
        """))

        # Create results table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS results (
                id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL,
                document_id TEXT NOT NULL,
                issuer TEXT,
                fields TEXT,
                raw_text TEXT,
                extraction_metadata TEXT,
                confidence_score REAL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (job_id) REFERENCES jobs(id),
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
        """))

    print("✓ Database initialized successfully")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_database())
