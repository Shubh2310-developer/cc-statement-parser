"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings, init_directories
from app.database.connection import init_db
from app.api.v1.router import api_router
from app.api.middleware import (
    configure_cors,
    register_exception_handlers,
    logging_middleware
)
from app.utils.logger import setup_logging, get_logger

# Initialize settings and logging
settings = get_settings()
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting CC Statement Parser API")
    init_directories()
    await init_db()
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    debug=settings.DEBUG
)

# Configure CORS
configure_cors(app)

# Add middleware
app.middleware("http")(logging_middleware)

# Register exception handlers
register_exception_handlers(app)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
