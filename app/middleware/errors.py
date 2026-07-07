from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.exceptions import (
    DiagnosisException,
    ValidationError,
    DatasetTooLarge,
    InvalidCSV,
    InvalidEncoding,
    UnsupportedFormat,
    EmptyDataset,
    DatasetNotFound,
    StorageFailure,
    DatabaseError,
    AnalyticsError,
    AIError
)
from app.core.logging import logger


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers custom exception handlers on the FastAPI application instance
    to convert domain exceptions into standard API responses.
    """

    @app.exception_handler(DatasetNotFound)
    async def dataset_not_found_handler(request: Request, exc: DatasetNotFound):
        logger.warning(f"DatasetNotFound: {exc.message} for route {request.url.path}")
        return JSONResponse(
            status_code=404,
            content={
                "error": "DatasetNotFound",
                "message": exc.message,
                "details": exc.details
            }
        )

    @app.exception_handler(DatasetTooLarge)
    async def dataset_too_large_handler(request: Request, exc: DatasetTooLarge):
        logger.warning(f"DatasetTooLarge: {exc.message} for route {request.url.path}")
        return JSONResponse(
            status_code=413,
            content={
                "error": "DatasetTooLarge",
                "message": exc.message,
                "details": exc.details
            }
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        logger.warning(f"ValidationError: {exc.message} on route {request.url.path}")
        return JSONResponse(
            status_code=422,
            content={
                "error": exc.__class__.__name__,
                "message": exc.message,
                "details": exc.details
            }
        )

    @app.exception_handler(StorageFailure)
    async def storage_failure_handler(request: Request, exc: StorageFailure):
        logger.error(f"StorageFailure: {exc.message} on route {request.url.path}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "StorageFailure",
                "message": "A storage operations error occurred in the backend.",
                "details": exc.details if app.debug else {}
            }
        )

    @app.exception_handler(DatabaseError)
    async def database_error_handler(request: Request, exc: DatabaseError):
        logger.error(f"DatabaseError: {exc.message} on route {request.url.path}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "DatabaseError",
                "message": "A database/data warehouse operations error occurred.",
                "details": exc.details if app.debug else {}
            }
        )

    @app.exception_handler(DiagnosisException)
    async def diagnosis_exception_handler(request: Request, exc: DiagnosisException):
        logger.error(f"DiagnosisException: {exc.message} on route {request.url.path}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": exc.__class__.__name__,
                "message": exc.message,
                "details": exc.details if app.debug else {}
            }
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.critical(f"Unhandled Exception: {str(exc)} on route {request.url.path}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "InternalServerError",
                "message": "An unexpected server error occurred.",
                "details": {"error_type": exc.__class__.__name__} if app.debug else {}
            }
        )
