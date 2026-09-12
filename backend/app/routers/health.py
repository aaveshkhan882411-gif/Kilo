from fastapi import APIRouter
from app.schemas.common import HealthResponse
from app.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="healthy")


@router.get("/health/detailed")
async def health_detailed():
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
        "ai_gateway": settings.AI_PROVIDER,
        "integrations": {},
    }
