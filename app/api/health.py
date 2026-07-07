from datetime import datetime, timezone
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/health", tags=["System"])
async def health_check():
    """
    Performs a lightweight system check, returning the application version,
    environment name, and current timestamp.
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
