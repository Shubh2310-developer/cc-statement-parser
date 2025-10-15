"""Request/response logging middleware."""
import time
import uuid
from fastapi import Request

from app.utils.logger import get_logger, set_request_id, clear_request_id

logger = get_logger(__name__)


async def logging_middleware(request: Request, call_next):
    """Log requests and responses."""
    request_id = str(uuid.uuid4())
    set_request_id(request_id)

    start_time = time.time()

    logger.info(
        f"Request started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
        }
    )

    try:
        response = await call_next(request)

        duration = time.time() - start_time

        logger.info(
            f"Request completed",
            extra={
                "request_id": request_id,
                "duration": f"{duration:.3f}s",
                "status_code": response.status_code,
            }
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response
    finally:
        clear_request_id()
