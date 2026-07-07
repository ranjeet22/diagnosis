from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import logger
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.errors import register_exception_handlers
from app.api import health
from app.api.v1 import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager managing FastAPI application lifecycle hooks.
    Fires on startup and shutdown events.
    """
    # Startup Hook
    logger.info(f"Bootstrapping {settings.APP_NAME} version {settings.APP_VERSION}...")
    logger.info(f"Environment: {settings.APP_ENV} | Debug Mode: {settings.DEBUG}")
    logger.info(f"Active Storage Provider: {settings.STORAGE_TYPE}")
    yield
    # Shutdown Hook
    logger.info(f"Initiating shutdown sequence for {settings.APP_NAME}...")
    logger.info("Application shutdown complete.")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Diagnōsis is a secure, production-grade Healthcare Analytics and Decision Support Platform backend.",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    debug=settings.DEBUG
)

# 1. Enable CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Enable Custom Request Logging Middleware
app.add_middleware(RequestLoggingMiddleware)

# 3. Register Global Custom Exception Handlers
register_exception_handlers(app)

# 4. Bind Application Routers
app.include_router(health.router)
app.include_router(v1_router.router, prefix="/api/v1")
