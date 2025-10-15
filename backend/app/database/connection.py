"""Database connection management."""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import get_settings
from app.database.models import Base
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # For SQLite
    poolclass=StaticPool,
    echo=settings.DEBUG,
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session():
    """Get database session for dependency injection."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    logger.info("Initializing database")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully")
