#!/usr/bin/env python3
"""Simple database initialization script that avoids unnecessary imports."""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Only import what we need for database init
async def init_database():
    """Initialize database without loading the entire app."""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
    from sqlalchemy import text
    import structlog

    logger = structlog.get_logger()

    # Database URL
    db_path = backend_dir / "data" / "db" / "cc_parser.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    database_url = f"sqlite+aiosqlite:///{db_path}"

    logger.info("Initializing database", url=database_url)

    # Create engine
    engine = create_async_engine(
        database_url,
        echo=False,
        future=True
    )

    # Import Base to create tables
    from app.database.models import Base

    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database initialized successfully")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_database())
    print("Database initialized")
