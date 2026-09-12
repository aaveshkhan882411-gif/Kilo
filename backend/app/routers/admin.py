from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_superuser
from app.models.user import User
from app.schemas.organization import OrganizationResponse

router = APIRouter()


@router.get("/stats")
async def system_stats(current_user: User = Depends(get_current_superuser)):
    return {"users": 0, "organizations": 0, "agents": 20, "integrations": 0}


@router.get("/organizations", response_model=list[OrganizationResponse])
async def admin_organizations(current_user: User = Depends(get_current_superuser)):
    return []
