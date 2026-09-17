from datetime import datetime
from app.models.user import User
from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_active_user
from app.schemas.integration import IntegrationCreate, IntegrationUpdate, IntegrationResponse

router = APIRouter()


@router.get("/", response_model=list[IntegrationResponse])
async def list_integrations(current_user: User = Depends(get_current_active_user)):
    return []


@router.post("/", response_model=IntegrationResponse, status_code=201)
async def create_integration(
    integration_in: IntegrationCreate,
    current_user: User = Depends(get_current_active_user),
):
    return IntegrationResponse(id="", org_id=current_user.org_id, provider=integration_in.provider, config=integration_in.config, status="inactive", created_at=datetime.utcnow(), updated_at=datetime.utcnow())


@router.patch("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: str,
    integration_in: IntegrationUpdate,
    current_user: User = Depends(get_current_active_user),
):
    return IntegrationResponse(id=integration_id, org_id=current_user.org_id, provider="", config={}, status="inactive", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
