from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .config import settings
from .database import close_db
from .middleware.security import SecurityHeadersMiddleware
from .middleware.rate_limit import RateLimitMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting GrowthAI application")
    logger.info("Database schema is managed by Alembic migrations")
    yield
    logger.info("Shutting down GrowthAI application")
    await close_db()
    logger.info("Database connections closed")


app = FastAPI(
    title=settings.APP_NAME,
    description="GrowthAI — Autonomous AI Workforce for Every Business",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
    }


@app.get("/")
async def root():
    return {
        "product": "GrowthAI",
        "tagline": "AI That Works. Systems That Evolve.",
        "version": settings.APP_VERSION,
    }


# Routers will be included here after creation
from .routers import api_router
app.include_router(api_router, prefix=settings.API_PREFIX)
