"""Global error handler middleware."""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.utils.logger import get_logger
from app.utils.exceptions import CCParserError

logger = get_logger(__name__)


async def error_handler_middleware(request: Request, call_next):
    """Global error handler."""
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        logger.error(f"Unhandled error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal server error", "detail": str(exc)}
        )


def register_exception_handlers(app):
    """Register exception handlers."""

    @app.exception_handler(CCParserError)
    async def parser_error_handler(request: Request, exc: CCParserError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"message": exc.message, "details": exc.details}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"message": "Validation error", "details": exc.errors()}
        )
