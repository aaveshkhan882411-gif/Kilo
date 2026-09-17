from datetime import datetime
from app.models.user import User
from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_active_user
from app.schemas.outcome import OutcomeResponse, OutcomeLifecycleUpdate

router = APIRouter()


@router.get("/{entity_type}/{entity_id}", response_model=list[OutcomeResponse])
async def get_outcomes(
    entity_type: str,
    entity_id: str,
    current_user: User = Depends(get_current_active_user),
):
    return []


@router.patch("/{outcome_id}", response_model=OutcomeResponse)
async def update_outcome(
    outcome_id: str,
    update: OutcomeLifecycleUpdate,
    current_user: User = Depends(get_current_active_user),
):
    return OutcomeResponse(id=outcome_id, org_id=current_user.org_id, entity_type="", entity_id="", lifecycle_status=update.lifecycle_status, technical_status=update.technical_status, business_status=update.business_status, data=update.data, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
