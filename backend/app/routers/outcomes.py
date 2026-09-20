from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.database import get_db
from app.models import Outcome
from app.models.user import User
from app.schemas.outcome import OutcomeResponse, OutcomeLifecycleUpdate

router = APIRouter()


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


@router.get(
    "/{entity_type}/{entity_id}",
    response_model=list[OutcomeResponse],
)
async def get_outcomes(
    entity_type: str,
    entity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Outcome)
        .where(
            Outcome.org_id == current_user.org_id,
            Outcome.entity_type == entity_type,
            Outcome.entity_id == entity_id,
        )
        .order_by(Outcome.created_at.desc())
    )

    return result.scalars().all()


@router.patch("/{outcome_id}", response_model=OutcomeResponse)
async def update_outcome(
    outcome_id: str,
    update: OutcomeLifecycleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Outcome).where(
            Outcome.id == outcome_id,
            Outcome.org_id == current_user.org_id,
        )
    )
    outcome = result.scalar_one_or_none()

    if outcome is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outcome not found",
        )

    update_data = update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(outcome, field, value)

    outcome.updated_at = utc_now()

    await db.commit()
    await db.refresh(outcome)

    return outcome
